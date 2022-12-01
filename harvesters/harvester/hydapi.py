import time

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
    Well, WellLevelMeasurement, WellYieldMeasurement, WellQualityMeasurement
)


class Hydapi(BaseHarvester):
    """
    Harvester for https://hydapi.nve.no/
    Documentation of API : https://hydapi.nve.no/UserDocumentation/
    """
    api_key = None
    max_oldest_time = parser.parse('1800-01-01T00:00:00Z')
    parameters = {}
    resolution_time = 1440

    def __init__(self, harvester: Harvester, replace: bool = False,
                 original_id: str = None):
        self.parameters = {
            1001: {
                'model': WellYieldMeasurement,
                'parameter': TermMeasurementParameter.objects.get(
                    name='Spring discharge')
            },
            1003: {
                'model': WellQualityMeasurement,
                'parameter': TermMeasurementParameter.objects.get(
                    name='T')
            },
            # just get the Instantenous
            5130: {
                'model': WellLevelMeasurement,
                'parameter': TermMeasurementParameter.objects.get(
                    name=MEASUREMENT_PARAMETER_GROUND)
            },
        }
        super(Hydapi, self).__init__(harvester, replace, original_id)

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
        stations = self._request_api('https://hydapi.nve.no/api/v1/Stations')[
            'data']
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
        # check available parameters
        # check start date
        parameter_ids = [
            series['parameter'] for series in station['seriesList']
        ]
        series_list = []
        for series in station['seriesList']:
            if series['parameter'] in self.parameters.keys():
                series_list.append(series)

        # Skip if no series that are needed
        if not series_list:
            self._update(f"Skip {station['stationId']} : {parameter_ids}")
            return

        self._update(f"Found {station['stationId']} : {parameter_ids}")

        # create well
        if self.original_id and station['stationId'] != self.original_id:
            return
        try:
            well, harvester_well_data = self._save_well(
                station['stationId'],
                station['stationName'],
                station['latitude'],
                station['longitude'],
                ground_surface_elevation_masl=station['masl']
            )
        except Well.DoesNotExist:
            return

        for series in series_list:
            # Check the latest from and to date
            parameter = series['parameter']
            measurement_parameter = self.parameters[parameter]
            model = measurement_parameter['model']

            # check latest date
            latest_measurement = model.objects.filter(
                well=harvester_well_data.well,
                parameter=measurement_parameter['parameter']
            ).order_by('-time').first()

            # Change the from and to time based on the measurements
            if not latest_measurement:
                harvester_well_data.from_time_data = self.max_oldest_time
            else:
                if not harvester_well_data.from_time_data:
                    harvester_well_data.from_time_data = latest_measurement.time

                if latest_measurement.time > harvester_well_data.from_time_data:
                    harvester_well_data.from_time_data = latest_measurement.time

            # CHeck if from date is less than the series
            for resolution in series['resolutionList']:
                if resolution['resTime'] == self.resolution_time:
                    date_from = parser.parse(resolution['dataFromTime'])
                    if harvester_well_data.from_time_data < date_from:
                        harvester_well_data.from_time_data = date_from

            harvester_well_data.save()

            self._fetch_measurements(
                station, harvester_well_data,
                harvester_well_data.from_time_data, series
            )

        # generate cache
        self.post_processing_well(well)

    def _fetch_measurements(
            self,
            station: dict,
            harvester_well_data: HarvesterWellData,
            from_date,
            series: dict):
        """ Processing older measurements """
        try:
            parameter = series['parameter']
            measurement_parameter = self.parameters[parameter]
            model = measurement_parameter['model']

            # check from and to date
            to_date = from_date + relativedelta(months=2)

            is_last = False
            now = timezone.now()
            if to_date > now:
                to_date = now
                is_last = True

            from_date_str = from_date.astimezone(
                pytz.utc
            ).replace(microsecond=0).isoformat().split('+')[0] + 'Z'
            to_date_str = to_date.astimezone(
                pytz.utc
            ).replace(microsecond=0).isoformat().split('+')[0] + 'Z'
            self._update(
                f"{station['stationId']} : {parameter} "
                f"- {from_date_str} - {to_date_str}"
            )
            # Fetch measurements data
            params = [
                f"StationId={station['stationId']}",
                f"Parameter={parameter}",
                f"ResolutionTime={self.resolution_time}",
                f'ReferenceTime={from_date_str}/{to_date_str}'
            ]
            url = 'https://hydapi.nve.no/api/v1/Observations?{}'.format(
                '&'.join(params)
            )
            try:
                response = self._request_api(url)
                for data in response['data']:
                    method = data['method']
                    try:
                        unit = Unit.objects.get(name=data['unit'])
                        for measurement in data['observations']:
                            if measurement['value'] is not None:
                                value = measurement['value']

                                # specifically based on parameter
                                if parameter == 5130:
                                    value = abs(value)

                                defaults = {
                                    'methodology': method,
                                    'parameter': measurement_parameter[
                                        'parameter']
                                }
                                if model == WellLevelMeasurement:
                                    defaults['value_in_m'] = value
                                obj = self._save_measurement(
                                    model,
                                    parser.parse(measurement['time']),
                                    defaults,
                                    harvester_well_data
                                )
                                if not obj.value:
                                    obj.value = Quantity.objects.create(
                                        unit=unit,
                                        value=value
                                    )
                                    obj.save()

                    except Unit.DoesNotExist as e:
                        print(f'{e}')
            except Exception:
                pass
            harvester_well_data.from_time_data = to_date
            harvester_well_data.save()

            if not is_last:
                time.sleep(1)
                self._fetch_measurements(
                    station, harvester_well_data, to_date, series
                )
        except KeyError:
            pass
