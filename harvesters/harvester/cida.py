"""Harvester of using Cida."""

import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse

from gwml2.harvesters.harvester.base import BaseHarvester
from gwml2.harvesters.models.harvester import Harvester
from gwml2.models.general import Unit, Quantity
from gwml2.models.geology import Geology
from gwml2.models.management import Management
from gwml2.models.term import (
    TermConfinement, TermReferenceElevationType, TermWellPurpose
)
from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.models.well import (
    Well,
    MEASUREMENT_PARAMETER_GROUND, WellLevelMeasurement, HydrogeologyParameter
)


class CidaUsgs(BaseHarvester):
    """
    Harvester for https://cida.usgs.gov/ngwmn/index.jsp
    """
    units = {}
    updated = False

    def __init__(
            self, harvester: Harvester, replace: bool = False,
            original_id: str = None
    ):
        try:
            self.units['feet'] = Unit.objects.get(name='ft')
            self.units['ft'] = Unit.objects.get(name='ft')
            self.units['m'] = Unit.objects.get(name='m')
        except Unit.DoesNotExist:
            pass

        self.parameter = TermMeasurementParameter.objects.get(
            name=MEASUREMENT_PARAMETER_GROUND
        )
        try:
            self.purpose = TermWellPurpose.objects.get(
                name='Observation / monitoring'
            )
        except TermWellPurpose.DoesNotExist:
            self.purpose = None
        super(CidaUsgs, self).__init__(harvester, replace, original_id)

    def _process(self):
        url = (
            f'https://cida.usgs.gov/ngwmn/geoserver/wfs?'
            f'request=GetFeature&SERVICE=WFS&VERSION=1.0.0&srsName=EPSG%3A4326&outputFormat=GML2&typeName=ngwmn%3AVW_GWDP_GEOSERVER&CQL_FILTER=((WL_SN_FLAG%20%3D%20%271%27)%20AND%20(WL_WELL_TYPE%20%3D%20%272%27))'
        )
        response = requests.get(url)
        if response.status_code == 200:
            print('Stations received')
            self.get_stations(BeautifulSoup(response.content, "lxml"))
            self._done()
        else:
            self._error(f'{response.status_code} - {response.text}')

    def value_by_tag(self, xml, tag):
        """Return value by tag"""
        return xml.find(tag).text

    def change_value_to_meter(self, value, unit):
        """Return value to meter"""
        if unit == self.units['feet']:
            return value * 0.3048, self.units['m']
        else:
            return value, self.units['m']

    def get_stations(self, xml):
        """Get stations list from featuremember."""
        members = xml.findAll('gml:featuremember')
        count = len(members)
        skip = True if self.original_id else False
        for idx, member in enumerate(members):
            self.updated = False
            site_no = self.value_by_tag(member, 'ngwmn:site_no')
            site_id = self.value_by_tag(member, 'ngwmn:my_siteid')
            message = f'{idx + 1}/{count} - {site_id}'
            self._update(message)
            if skip:
                if site_no == self.original_id:
                    skip = False
                else:
                    continue
            try:
                site_name = self.value_by_tag(member, 'ngwmn:site_name')
                latitude = float(
                    self.value_by_tag(member, 'ngwmn:dec_lat_va')
                )
                longitude = float(
                    self.value_by_tag(member, 'ngwmn:dec_long_va')
                )
                altitude = float(
                    self.value_by_tag(member, 'ngwmn:alt_va')
                )
                altitude_unit = self.units[
                    self.value_by_tag(member, 'ngwmn:alt_units_nm').lower()
                ]
                altitude, unit = self.change_value_to_meter(
                    altitude, altitude_unit
                )
                agency_name = self.value_by_tag(member, 'ngwmn:agency_nm')
                agency_code = self.value_by_tag(member, 'ngwmn:agency_cd')

                well_data = {
                    'site_id': site_id,
                    'site_no': site_no,
                    'site_name': site_name,
                    'latitude': latitude,
                    'longitude': longitude,
                    'altitude': altitude,
                    'agency_name': agency_name,
                    'agency_code': agency_code,
                    'unit': self.unit_m
                }
                # Save well
                well, harvester_well_data = self._save_well(
                    original_id=site_no,
                    name=site_name,
                    latitude=latitude,
                    longitude=longitude,
                    ground_surface_elevation_masl=altitude
                )

                # Total depth
                if not well.geology:
                    try:
                        well_depth = float(
                            self.value_by_tag(
                                member, 'ngwmn:well_depth')
                        )
                        well_depth_unit = self.units[
                            self.value_by_tag(
                                member, 'ngwmn:well_depth_units_nm'
                            ).lower()
                        ]
                        well_depth, well_depth_unit = self.change_value_to_meter(
                            well_depth, well_depth_unit
                        )
                        elevation_type = TermReferenceElevationType.objects.get(
                            name='Ground Surface Level ASL')
                        well.geology = Geology.objects.create(
                            total_depth=Quantity.objects.create(
                                value=well_depth,
                                unit=well_depth_unit
                            ),
                            reference_elevation=elevation_type
                        )
                    except (
                            KeyError, AttributeError,
                            TermReferenceElevationType.DoesNotExist
                    ):
                        pass
                if not well.hydrogeology_parameter:
                    # Confinement
                    confinement = self.value_by_tag(member, 'ngwmn:aqfr_char')
                    try:
                        confinement = TermConfinement.objects.get(
                            name__iexact=confinement.lower())
                        well.hydrogeology_parameter = HydrogeologyParameter.objects.create(
                            aquifer_name=self.value_by_tag(
                                member, 'ngwmn:local_aquifer_name'),
                            confinement=confinement,

                        )
                    except (AttributeError, TermConfinement.DoesNotExist):
                        pass

                detail = (
                    f'https://cida.usgs.gov/ngwmn/provider/'
                    f'{well_data["agency_code"]}/site/{well_data["site_no"]}/'
                )
                if not well.purpose:
                    well.purpose = self.purpose
                if not well.description:
                    well.description = detail

                # Save management
                if not well.management:
                    management = Management.objects.create(
                        manager=agency_name
                    )
                    well.management = management
                well.save()

                # Save measurements
                self.get_measurements(well_data, harvester_well_data)

                # Generate cache
                if self.updated:
                    self.post_processing_well(well)
            except (KeyError, Well.DoesNotExist):
                pass
            except Exception as e:
                raise Exception(f'{site_id} : {e}')

    def get_measurements(self, well_data, harvester_well_data):
        """Get and save measurements."""
        url = (
            f'https://cida.usgs.gov/ngwmn_cache/direct/flatXML/waterlevel/'
            f'{well_data["agency_code"]}/{well_data["site_no"]}'
        )
        response = requests.get(url)
        if response.status_code != 200:
            print('Measurements not found')
        else:
            xml = BeautifulSoup(response.content, "lxml")
            samples = xml.findAll('sample')
            count = len(samples)
            print(f'Measurements found : {count}')
            last_time = None
            last_data = harvester_well_data.well.welllevelmeasurement_set.all().first()
            if last_data:
                last_time = last_data.time

            for idx, measurement in enumerate(samples):
                try:
                    time = self.value_by_tag(measurement, 'time')
                    time = parse(time)
                    if last_time and time <= last_time:
                        continue

                    print(f'{idx}/{count} - {time}')
                    unit = self.units[
                        self.value_by_tag(measurement, 'unit').lower()
                    ]
                    value = float(
                        self.value_by_tag(
                            measurement, 'from-landsurface-value'
                        )
                    )
                    value, unit = self.change_value_to_meter(value, unit)
                    defaults = {
                        'parameter': self.parameter
                    }
                    self._save_measurement(
                        WellLevelMeasurement,
                        time,
                        defaults,
                        harvester_well_data,
                        value,
                        unit
                    )
                    self.updated = True
                except (ValueError, KeyError, TypeError) as e:
                    pass