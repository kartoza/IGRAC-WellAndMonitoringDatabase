import time

import pytz
from dateutil import parser
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from gwml2.harvesters.harvester.base import BaseHarvester
from gwml2.harvesters.models.harvester import (
    HarvesterParameterMap, HarvesterWellData, Harvester, HarvesterAttribute
)
from gwml2.models.general import Quantity, Unit
from gwml2.models.term import TermWellStatus
from gwml2.models.term_measurement_parameter import (
    TermMeasurementParameterGroup, TermMeasurementParameter
)
from gwml2.models.well import (
    MEASUREMENT_PARAMETER_GROUND,
    Well, WellLevelMeasurement
)

STATIONSID_KEY = 'stationsid'


class Hydapi(BaseHarvester):
    """
    Harvester for https://hydapi.nve.no/
    Documentation of API : https://hydapi.nve.no/UserDocumentation/
    """
    api_key = None
    max_oldest_time = parser.parse('1800-01-01T00:00:00Z')
    parameters = {}
    updated = False

    def default_parameters(self, harvester: Harvester):
        """This is for legacy one."""
        HarvesterParameterMap.objects.get_or_create(
            harvester=harvester,
            key='1001',
            defaults={
                'parameter': TermMeasurementParameter.objects.get(
                    name='Spring discharge'
                ),
                'unit': Unit.objects.get(name='m³/s')
            }
        )
        HarvesterParameterMap.objects.get_or_create(
            harvester=harvester,
            key='2015',
            defaults={
                'parameter': TermMeasurementParameter.objects.get(
                    name='T'
                ),
                'unit': Unit.objects.get(name='°C')
            }
        )
        HarvesterParameterMap.objects.get_or_create(
            harvester=harvester,
            key='5130',
            defaults={
                'parameter': TermMeasurementParameter.objects.get(
                    name=MEASUREMENT_PARAMETER_GROUND
                ),
                'unit': Unit.objects.get(name='m')
            }
        )

    def __init__(
            self, harvester: Harvester, replace: bool = False,
            original_id: str = None
    ):
        self.default_parameters(harvester)
        self.parameters = HarvesterParameterMap.get_json(harvester)
        self.parameters = {
            int(key): value for key, value in self.parameters.items()
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

        # Previous station id
        previous_station = None
        try:
            previous_station = HarvesterAttribute.objects.get(
                harvester=self.harvester,
                name=STATIONSID_KEY
            ).value
        except (HarvesterAttribute.DoesNotExist, AttributeError):
            pass

        # fetch stations first
        stations = self._request_api('https://hydapi.nve.no/api/v1/Stations')[
            'data']
        for station in stations:
            # Current stationid
            stationsid = station['stationId']

            # If not same with previous stationid, skip it.
            if previous_station and stationsid != previous_station:
                continue

            previous_station = None

            # Save as previous stationid
            HarvesterAttribute.objects.update_or_create(
                harvester=self.harvester,
                name=STATIONSID_KEY,
                defaults={
                    'value': stationsid,
                }
            )

            # Process station
            self._process_station(station)

    def _process_station(self, station: dict):
        """
        Processing a station
        Save it to well
        Save it as HarvesterWellData
        Fetch measurement
        """
        # check available parameters
        # check start date
        self.updated = False
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
            status = None
            try:
                if station['stationStatusName'] == 'Aktiv':
                    status = TermWellStatus.objects.get(
                        name__iexact='Active'
                    )
            except TermWellStatus.DoesNotExist:
                pass
            well.status = status
            well.save()
        except Well.DoesNotExist:
            return

        for series in series_list:
            # Check the latest from and to date
            parameter = series['parameter']
            try:
                _parameter = self.parameters[parameter]
                parameter = _parameter['parameter']
                unit = _parameter['unit']
                model = (
                    TermMeasurementParameterGroup.get_measurement_model(
                        parameter
                    )
                )
            except KeyError:
                continue

            # check latest date
            latest_measurement = model.objects.filter(
                well=harvester_well_data.well,
                parameter=parameter
            ).order_by('-time').first()

            # Change the from and to time based on the measurements
            if not latest_measurement:
                from_time_data = self.max_oldest_time
            else:
                from_time_data = latest_measurement.time

            # Get resolution time
            resolution_time = None
            for resolution in series['resolutionList']:
                if resolution['resTime'] == 1440:
                    resolution_time = resolution
            if not resolution_time:
                for resolution in series['resolutionList']:
                    if resolution['resTime'] == 60:
                        resolution_time = resolution

            # If resolution time is exist
            if resolution_time:
                date_from = parser.parse(resolution_time['dataFromTime'])
                if from_time_data < date_from:
                    from_time_data = date_from

                self._fetch_measurements(
                    station, harvester_well_data,
                    from_time_data, series, resolution_time['resTime'],

                    # Parameter data
                    model,
                    parameter,
                    unit
                )

        # generate cache
        if self.updated:
            self.post_processing_well(well)

    def _fetch_measurements(
            self,
            station: dict,
            harvester_well_data: HarvesterWellData,
            from_date,
            series: dict,
            resolution_time: int,

            # Parameter data
            model,
            parameter,
            unit
    ):
        """ Processing older measurements """
        try:
            parameter_key = series['parameter']

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
                f"{station['stationId']} : {parameter_key} "
                f"({series.get('parameterName', 'no parameter name')}) "
                f"- {from_date_str} - {to_date_str}"
            )
            # Fetch measurements data
            params = [
                f"StationId={station['stationId']}",
                f"Parameter={parameter_key}",
                f"ResolutionTime={resolution_time}",
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
                        for measurement in data['observations']:
                            if measurement['value'] is not None:
                                value = measurement['value']

                                # specifically based on parameter
                                if parameter_key == 5130:
                                    value = abs(value)

                                defaults = {
                                    'methodology': method,
                                    'parameter': parameter
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
                                self.updated = True

                    except Unit.DoesNotExist as e:
                        print(f'{e}')
            except Exception:
                pass

            if not is_last:
                time.sleep(1)
                self._fetch_measurements(
                    station, harvester_well_data, to_date, series,
                    resolution_time,

                    # Parameter data
                    model,
                    parameter,
                    unit
                )
        except KeyError:
            pass
