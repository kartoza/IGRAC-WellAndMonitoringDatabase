import pytz
from dateutil import parser
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from gwml2.harvesters.harvester.base import BaseHarvester
from gwml2.harvesters.models.harvester import Harvester, HarvesterWellData
from gwml2.models.general import Quantity, Unit
from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.models.well import (
    MEASUREMENT_PARAMETER_GROUND,
    WellLevelMeasurement, WellQualityMeasurement, WellYieldMeasurement
)
from gwml2.tasks.well import generate_measurement_cache


class Hydapi(BaseHarvester):
    """
    Harvester for https://hydapi.nve.no/
    Documentation of API : https://hydapi.nve.no/UserDocumentation/
    """
    api_key = None
    max_oldest_time = parser.parse('2000-01-01T00:00:00Z')
    parameters = {}

    def __init__(self, harvester: Harvester):
        self.parameters = {
            1000: {
                'model': WellLevelMeasurement,
                'parameter': TermMeasurementParameter.objects.get(
                    name=MEASUREMENT_PARAMETER_GROUND)
            },
            1003: {
                'model': WellQualityMeasurement,
                'parameter': TermMeasurementParameter.objects.get(name='T')
            }
        }
        super(Hydapi, self).__init__(harvester)

    @staticmethod
    def additional_attributes() -> dict:
        """
        Attributes that needs to be saved on database
        The value is the default value for the attribute
        """
        return {
            'x-api-key': None
        }

    @property
    def _headers(self) -> dict:
        return {'x-api-key': self.api_key}

    def _process(self):
        """ Run the harvester """
        # check the api key is presented or not
        try:
            self.api_key = self.attributes['x-api-key']
        except KeyError:
            pass

        if not self.api_key:
            raise Exception('Api key is not provided.')

        # fetch stations first
        stations = self._request_api('https://hydapi.nve.no/api/v1/Stations')['data']
        for station in stations:
            self._process_station(station)
        self._done('Done')

    def _process_station(self, station: dict):
        """
        Processing a station
        Save it to well
        Save it as HarvesterWellData
        Fetch measurement
        """
        # create well
        well, harvester_well_data = self._save_well(
            station['stationId'],
            station['stationName'],
            station['latitude'],
            station['longitude'],
            ground_surface_elevation_masl=station['masl']
        )
        harvester_well_data.from_time_data = self.max_oldest_time
        harvester_well_data.save()

        # check available parameters
        # check start date
        series_list = station['seriesList']
        parameters = []
        for series in series_list:
            # just get the Instantenous
            parameters.append(series['parameter'])
            for resolution in series['resolutionList']:
                if resolution['resTime'] == 0:
                    date_from = parser.parse(resolution['dataFromTime'])
                    if harvester_well_data.from_time_data < date_from:
                        harvester_well_data.from_time_data = date_from
                        harvester_well_data.save()

        self.fetch_measurements(station, harvester_well_data, parameters)

        # generate cache
        generate_measurement_cache(
            well.id, WellLevelMeasurement.__name__)
        generate_measurement_cache(
            well.id, WellQualityMeasurement.__name__)
        generate_measurement_cache(
            well.id, WellYieldMeasurement.__name__)

    def fetch_measurements(
            self,
            station: dict,
            harvester_well_data: HarvesterWellData,
            parameters: list):
        """ Processing older measurements """

        # check from and to date
        from_date = harvester_well_data.from_time_data
        if harvester_well_data.to_time_data:
            from_date = harvester_well_data.to_time_data
        to_date = from_date + relativedelta(months=1)

        is_last = False
        now = timezone.now()
        if to_date > now:
            to_date = now
            is_last = True

        from_date_str = from_date.astimezone(
            pytz.utc).replace(microsecond=0).isoformat().split('+')[0] + 'Z'
        to_date_str = to_date.astimezone(
            pytz.utc).replace(microsecond=0).isoformat().split('+')[0] + 'Z'
        self._update('{} : {} - {}'.format(
            station['stationId'], from_date_str, to_date_str))
        for parameter in parameters:
            try:
                measurement_parameter = self.parameters[parameter]
                model = measurement_parameter['model']
                params = [
                    'StationId={}'.format(station['stationId']),
                    'Parameter={}'.format(parameter),
                    'ResolutionTime=0',
                    'ReferenceTime={from_date}/{to_date}'.format(
                        from_date=from_date_str,
                        to_date=to_date_str
                    )
                ]
                url = 'https://hydapi.nve.no/api/v1/Observations?{}'.format(
                    '&'.join(params)
                )
                response = self._request_api(url)
                for data in response['data']:
                    method = data['method']
                    try:
                        unit = Unit.objects.get(name=data['unit'])
                        for measurement in data['observations']:
                            if measurement['value'] is not None:
                                defaults = {
                                    'methodology': method,
                                    'parameter': measurement_parameter['parameter']
                                }
                                if model == WellLevelMeasurement:
                                    defaults['value_in_m'] = measurement['value']
                                obj = self._save_measurement(
                                    model,
                                    parser.parse(measurement['time']),
                                    defaults,
                                    harvester_well_data
                                )
                                if not obj.value:
                                    obj.value = Quantity.objects.create(
                                        unit=unit,
                                        value=measurement['value']
                                    )
                                    obj.save()

                    except Unit.DoesNotExist as e:
                        print('{}'.format(e))
            except KeyError:
                pass
        harvester_well_data.to_time_data = to_date
        harvester_well_data.save()

        if not is_last:
            self.fetch_measurements(station, harvester_well_data, parameters)
