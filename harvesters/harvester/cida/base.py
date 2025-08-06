"""Harvester of using Cida."""

import requests
from bs4 import BeautifulSoup

from gwml2.harvesters.harvester.base import BaseHarvester
from gwml2.harvesters.models.harvester import Harvester
from gwml2.models.general import Unit, Quantity
from gwml2.models.geology import Geology
from gwml2.models.management import Management
from gwml2.models.term import (
    TermConfinement, TermReferenceElevationType, TermWellPurpose
)
from gwml2.models.well import (
    Well, HydrogeologyParameter
)
from gwml2.tasks.data_file_cache.country_recache import (
    generate_data_country_cache
)


class CidaUsgsApi(BaseHarvester):
    """Harvester for https://cida.usgs.gov/ngwmn/index.jsp."""

    units = {}
    updated = False
    last_code_key = 'last-code'
    proceed = False
    retry = 0

    @staticmethod
    def cql_filter_method():
        """Return station url."""
        raise NotImplementedError

    @property
    def cql_filter(self):
        """Return station url."""
        raise NotImplementedError

    def __init__(
            self, harvester: Harvester, replace: bool = False,
            original_id: str = None
    ):
        try:
            self.units['feet'] = Unit.objects.get(name='ft')
            self.units['ft'] = Unit.objects.get(name='ft')
            self.units['m'] = Unit.objects.get(name='m')
            self.units['meters'] = Unit.objects.get(name='m')
            self.units['centimeters'] = Unit.objects.get(name='cm')
        except Unit.DoesNotExist:
            pass
        try:
            self.purpose = TermWellPurpose.objects.get(
                name='Observation / monitoring'
            )
        except TermWellPurpose.DoesNotExist:
            self.purpose = None
        super(CidaUsgsApi, self).__init__(harvester, replace, original_id)

    def clean_process(self):
        """Clean process."""
        from .level import CidaUsgsWaterLevel
        from .quality import CidaUsgsWaterQuality

        self._update('Cleaning process...')
        station_url = (
            "https://www.usgs.gov/apps/ngwmn/geoserver/ngwmn/wfs?request=GetFeature&SERVICE=WFS&VERSION=1.1.0&srsName=EPSG:4326&outputFormat=GML2&typeName=ngwmn:VW_GWDP_GEOSERVER&"
            f"CQL_FILTER={CidaUsgsWaterLevel.cql_filter_method()} OR {CidaUsgsWaterQuality.cql_filter_method()}"
        )
        try:
            response = requests.get(station_url)
            if response.status_code == 200:
                xml = BeautifulSoup(response.content, "lxml")
                members = xml.findAll('gml:featuremember')
                count = len(members)
                self._update(f'Found all members : {count}')

                # Get list of stations from server
                # Make all list of stations on server
                # but not on the response as none organisation
                # This is for the case when our well is being deleted from the sites
                sites = [
                    self.value_by_tag(member, 'ngwmn:site_no') for member in
                    members
                ]

                # Make the not found wells to none organisation
                Well.objects.filter(
                    organisation__id=self.harvester.organisation.id
                ).exclude(original_id__in=sites).update(organisation=None)
            else:
                self._error(f'{response.status_code} - {response.text}')
        except requests.exceptions.ConnectionError as e:
            self.retry += 1
            if self.retry == 3:
                raise Exception(e)
            else:
                self._process()

    def _process(self):
        # Check last code
        self.last_code = self.attributes.get(self.last_code_key, None)
        if not self.last_code:
            self.proceed = True

        # Clean process
        self.clean_process()
        self.retry = 1

        station_url = (
            "https://www.usgs.gov/apps/ngwmn/geoserver/ngwmn/wfs?request=GetFeature&SERVICE=WFS&VERSION=1.1.0&srsName=EPSG:4326&outputFormat=GML2&typeName=ngwmn:VW_GWDP_GEOSERVER&"
            f"CQL_FILTER={self.cql_filter}"
        )
        try:
            response = requests.get(station_url)
            if response.status_code == 200:
                self.get_stations(BeautifulSoup(response.content, "lxml"))
            else:
                self._error(f'{response.status_code} - {response.text}')
        except requests.exceptions.ConnectionError as e:
            self.retry += 1
            if self.retry == 3:
                raise Exception(e)
            else:
                self._process()

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

        # Run the harvesting
        # Skip if we have origi
        for idx, member in enumerate(members):
            self.updated = False
            site_no = self.value_by_tag(member, 'ngwmn:site_no')
            site_id = self.value_by_tag(member, 'ngwmn:my_siteid')
            message = f'{idx + 1}/{count} - {site_id}'
            self._update(message)

            # Check last code, if there, skip if not found yet
            if self.last_code:
                if site_no == self.last_code:
                    self.proceed = True

            if not self.proceed:
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
                    ground_surface_elevation_masl=altitude,
                    reassign_organisation=True
                )

                # Total depth
                if not well.geology:
                    try:
                        well_depth = float(
                            self.value_by_tag(
                                member, 'ngwmn:well_depth'
                            )
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
                            name='Ground Surface Level ASL'
                        )
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
                            name__iexact=confinement.lower()
                        )
                        well.hydrogeology_parameter = HydrogeologyParameter.objects.create(
                            aquifer_name=self.value_by_tag(
                                member, 'ngwmn:local_aquifer_name'
                            ),
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
                    self.post_processing_well(
                        well, generate_country_cache=False
                    )

                self.update_attribute(
                    self.last_code_key, site_no
                )
            except (
                    KeyError, Well.DoesNotExist,
                    requests.exceptions.ConnectionError
            ):
                pass
            except Exception as e:
                raise Exception(f'{site_id} : {e}')

        self.delete_attribute(self.last_code_key)

        # Run country caches
        self._update('Run country caches')
        generate_data_country_cache(self.harvester.organisation.country.code)

    def get_measurements(self, well_data, harvester_well_data):
        """Get and save measurements."""
        raise NotImplementedError()
