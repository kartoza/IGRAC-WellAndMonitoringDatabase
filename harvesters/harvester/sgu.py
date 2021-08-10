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
    MEASUREMENT_PARAMETER_GROUND,
    WellLevelMeasurement
)
from gwml2.tasks.well import generate_measurement_cache


class SguAPI(BaseHarvester):
    """
    Harvester for https://www.sgu.se/
    """
    max_region_codes = {

    }

    def __init__(self, harvester: Harvester):
        self.unit_m = Unit.objects.get(name='m')
        self.parameter = TermMeasurementParameter.objects.get(
            name=MEASUREMENT_PARAMETER_GROUND)
        super(SguAPI, self).__init__(harvester)

    @staticmethod
    def additional_attributes() -> dict:
        """
        Attributes that needs to be saved on database
        The value is the default value for the attribute
        """
        return {
            'min-region-code': 1,
            'max-region-code': 25
        }

    def _process(self):
        """ Run the harvester """
        try:
            self.min_region_code = self.attributes['min-region-code']
            self.max_region_code = self.attributes['max-region-code']
        except KeyError:
            pass
        for index in list(range(int(self.min_region_code), int(self.max_region_code))):
            url = 'https://resource.sgu.se/oppnadata/grundvatten/api/grundvattennivaer/nivaer/lan/{:02d}?format=json'.format(index)
            self._update('Fetching {}'.format(url))

            response = requests.get(url)
            if response.status_code == 404:
                continue
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
                to_coord = SpatialReference(4326)
                from_coord = SpatialReference(crs)
                trans = CoordTransform(from_coord, to_coord)
                well_total = len(data['features'])
                for well_idx, feature in enumerate(data['features']):
                    self._update(
                        'Saving {} : well({}/{})'.format(url, well_idx + 1, well_total)
                    )
                    coordinates = feature['geometry']['coordinates']
                    point = Point(coordinates[0], coordinates[1], srid=crs)
                    point.transform(trans)

                    # check the properties
                    properties = feature['properties']
                    original_id = properties['omrade-_och_stationsnummer']
                    name = properties['stationens_namn']
                    top_of_well_elevation = properties['referensniva_for_roroverkant_m_o.h.']
                    height_of_tube = properties['rorhojd_ovan_mark_m']
                    ground_surface_elevation = top_of_well_elevation - height_of_tube

                    well, harvester_well_data = self._save_well(
                        original_id=original_id,
                        name=name,
                        latitude=point.y,
                        longitude=point.x,
                        ground_surface_elevation_masl=ground_surface_elevation,
                        top_of_well_elevation_masl=top_of_well_elevation
                    )
                    measurement_total = len(properties['Mätningar'])
                    for measurement_idx, measurement in enumerate(properties['Mätningar']):
                        self._update('Saving {} : well({}/{}) measurement({}/{})'.format(
                            url, well_idx + 1, well_total, measurement_idx, measurement_total)
                        )
                        try:
                            defaults = {
                                'parameter': self.parameter,
                                'value_in_m': measurement['grundvattenniva_m_under_markyta']
                            }
                            obj = self._save_measurement(
                                WellLevelMeasurement,
                                make_aware(parser.parse(measurement['datum_for_matning'])),
                                defaults,
                                harvester_well_data
                            )
                            if not obj.value:
                                obj.value = Quantity.objects.create(
                                    unit=self.unit_m,
                                    value=measurement['grundvattenniva_m_under_markyta']
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
