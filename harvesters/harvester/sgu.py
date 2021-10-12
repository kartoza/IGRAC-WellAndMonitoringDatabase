import json
import os
import requests
from dateutil import parser
from django.contrib.gis.gdal import SpatialReference, CoordTransform
from django.contrib.gis.geos import Point
from django.utils.timezone import make_aware
from gwml2.harvesters.harvester.base import BaseHarvester
from gwml2.harvesters.models.harvester import Harvester
from gwml2.models.general import Quantity, Unit
from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.models.well import (
    MEASUREMENT_PARAMETER_AMSL,
    Well, WellLevelMeasurement
)
from gwml2.tasks.well import generate_measurement_cache


class SguAPI(BaseHarvester):
    """
    Harvester for https://www.sgu.se/
    """
    max_region_codes = {

    }

    def __init__(self, harvester: Harvester, replace: bool = False, original_id: str = None):
        self.unit_m = Unit.objects.get(name='m')
        self.parameter = TermMeasurementParameter.objects.get(
            name=MEASUREMENT_PARAMETER_AMSL)
        super(SguAPI, self).__init__(harvester, replace, original_id)

    @staticmethod
    def additional_attributes() -> dict:
        """
        Attributes that needs to be saved on database
        The value is the default value for the attribute
        """
        return {}

    def _process(self):
        """ Run the harvester """
        url = 'https://apps.sgu.se/grundvattennivaer-rest/stationer'
        self._update('Fetching {}'.format(url))

        response = requests.get(url)
        if response.status_code == 404:
            return

        try:
            os.remove('sgu.json')
        except IOError:
            pass

        with open('sgu.json', 'w') as fd:
            fd.write(response.text)

        data = json.load(open('sgu.json'))
        try:
            # get csr
            crs = data['crs']['properties']['name']
            well_total = len(data['features'])
            for well_idx, station in enumerate(data['features']):
                to_coord = SpatialReference(4326)
                from_coord = SpatialReference(crs)
                trans = CoordTransform(from_coord, to_coord)
                try:
                    coordinates = station['geometry']['coordinates']
                except (KeyError, TypeError):
                    continue

                point = Point(coordinates[0], coordinates[1], srid=crs)
                point.transform(trans)

                # check the station
                station_id = station['properties']['OMR_STN']
                name = station['properties']['STN_NAMN']
                try:
                    well, harvester_well_data = self._save_well(
                        original_id=station_id,
                        name=name,
                        latitude=point.y,
                        longitude=point.x,
                    )
                except Well.DoesNotExist:
                    continue

                # get measurements
                response = self._request_api(f'https://resource.sgu.se/oppnadata/grundvatten/api/grundvattennivaer/nivaer/station/{station_id}?format=json')
                try:
                    feature = response['features'][0]
                except IndexError:
                    continue

                properties = feature['properties']
                original_id = properties['omrade-_och_stationsnummer']

                # skip if it does not return same station id
                if station_id != original_id:
                    continue

                self._update(
                    'Saving {} : well({}/{})'.format(url, well_idx + 1, well_total)
                )

                # check latest date
                latest_measurement = WellLevelMeasurement.objects.filter(
                    well=harvester_well_data.well,
                ).order_by('-time').first()

                measurement_total = len(properties['Mätningar'])
                for measurement_idx, measurement in enumerate(properties['Mätningar']):
                    try:
                        date_time = make_aware(parser.parse(measurement['datum_for_matning']))
                        if not latest_measurement or date_time > latest_measurement.time:
                            self._update('Saving {} : well({}/{}) measurement({}/{})'.format(
                                url, well_idx + 1, well_total, measurement_idx, measurement_total)
                            )
                            defaults = {
                                'parameter': self.parameter,
                                'value_in_m': measurement['grundvattenniva_m_o.h.']
                            }
                            obj = self._save_measurement(
                                WellLevelMeasurement,
                                date_time,
                                defaults,
                                harvester_well_data
                            )
                            if not obj.value:
                                obj.value = Quantity.objects.create(
                                    unit=self.unit_m,
                                    value=measurement['grundvattenniva_m_o.h.']
                                )
                                obj.save()
                    except KeyError:
                        pass
                generate_measurement_cache(
                    well.id, WellLevelMeasurement.__name__)
        except KeyError as e:
            pass
        try:
            os.remove('sgu.json')
        except IOError:
            pass
        self._done('Done')
