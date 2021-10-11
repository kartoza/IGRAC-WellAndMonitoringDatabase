import pytz
import requests
import xml.etree.ElementTree as ET
from dateutil import parser
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from gwml2.harvesters.harvester.base import BaseHarvester
from gwml2.harvesters.models.harvester import Harvester, HarvesterWellData
from gwml2.models.general import Quantity, Unit
from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.models.well import (
    MEASUREMENT_PARAMETER_AMSL, Well, WellLevelMeasurement
)
from gwml2.tasks.well import generate_measurement_cache


class GinGWInfo(BaseHarvester):
    """
    Harvester for https://gin.gw-info.net/
    """
    url = 'https://gin.gw-info.net/GinService/sos/gw?REQUEST=GetFeatureOfInterest&VERSION=2.0.0&' \
          'SERVICE=SOS&spatialFilter=om:featureOfInterest/*/sams:shape,-180,-90,180,90,http://www.opengis.net/def/crs/EPSG/0/4326&' \
          'namespaces=xmlns(sams,http://www.opengis.net/samplingSpatial/2.0),xmlns(om,http://www.opengis.net/om/2.0)'
    sos = '{http://www.opengis.net/sos/2.0}'
    sams = '{http://www.opengis.net/samplingSpatial/2.0}'
    gml = '{http://www.opengis.net/gml/3.2}'
    om = '{http://www.opengis.net/om/2.0}'
    wml2 = '{http://www.opengis.net/waterml/2.0}'

    def __init__(self, harvester: Harvester, replace: bool = True, original_id: str = None):
        self.unit_m = Unit.objects.get(name='m')
        self.parameter = TermMeasurementParameter.objects.get(
            name=MEASUREMENT_PARAMETER_AMSL)
        super(GinGWInfo, self).__init__(harvester, replace, original_id)

    @staticmethod
    def additional_attributes() -> dict:
        """
        Attributes that needs to be saved on database
        The value is the default value for the attribute
        """
        return {}

    def _process(self):
        """ Run the harvester """
        self._stations()
        self._done('Done')

    def _stations(self):
        """ fetch and save wells """
        try:
            response = requests.get(self.url, headers=self._headers)
            response.raise_for_status()
        except (
                requests.exceptions.RequestException,
                requests.exceptions.HTTPError) as e:
            raise Exception('{} : {}'.format(self.url, e))
        else:
            tree = ET.fromstring(response.content)
            for feature_xml in tree.findall(f'{self.sos}featureMember'):
                try:
                    feature = feature_xml.find(f'{self.sams}SF_SpatialSamplingFeature')
                    id = feature.attrib[f'{self.gml}id']
                    description = feature.find(f"{self.gml}description").text
                    coordinates = feature.find(f"{self.sams}shape/{self.gml}Point/{self.gml}pos").text.split(' ')
                    coordinates = [float(coordinate) for coordinate in coordinates]
                    # create well
                    try:
                        well, harvester_well_data = self._save_well(
                            id,
                            id,
                            coordinates[0],
                            coordinates[1],
                            description=description
                        )
                        self._measurements(well, harvester_well_data)
                        generate_measurement_cache(
                            well.id, WellLevelMeasurement.__name__)
                    except Well.DoesNotExist:
                        continue
                except AttributeError:
                    pass

    def _measurements(
            self,
            well: Well,
            harvester_well_data: HarvesterWellData):
        """ fetch and save measurement of specific well """
        url = f'https://gin.gw-info.net/GinService/sos/gw?' \
            f'REQUEST=GetObservation&VERSION=2.0.0&SERVICE=SOS' \
            f'&offering=GW_LEVEL&featureOfInterest={well.original_id}&observedProperty=urn:ogc:def:phenomenon:OGC:1.0.30:groundwaterlevel'
        self._update(
            'Checking measurements {} : url = {}'.format(well.original_id, url)
        )
        try:
            response = requests.get(url, headers=self._headers)
            response.raise_for_status()
        except (
                requests.exceptions.RequestException,
                requests.exceptions.HTTPError) as e:
            return
        else:
            # check latest date
            latest_measurement = WellLevelMeasurement.objects.filter(
                well=harvester_well_data.well,
            ).order_by('-time').first()

            tree = ET.fromstring(response.content)
            measurements = tree.findall(f'{self.sos}observationData/{self.om}OM_Observation/{self.om}result/{self.wml2}MeasurementTimeSeries/{self.wml2}point')
            for measurement in measurements:
                time = measurement.find(f'{self.wml2}MeasurementTVP/{self.wml2}time').text
                value = measurement.find(f'{self.wml2}MeasurementTVP/{self.wml2}value').text
                time = parser.parse(time)
                if not latest_measurement or time > latest_measurement.time:
                    print(f'save: {time}')

                    defaults = {
                        'parameter': self.parameter,
                        'value_in_m': value
                    }
                    obj = self._save_measurement(
                        WellLevelMeasurement,
                        time,
                        defaults,
                        harvester_well_data
                    )
                    if not obj.value:
                        obj.value = Quantity.objects.create(
                            unit=self.unit_m,
                            value=value
                        )
                        obj.save()
