import requests
from dateutil import parser
from django.contrib.gis.gdal import SpatialReference, CoordTransform
from django.contrib.gis.geos import Point
from django.utils.timezone import make_aware

from gwml2.harvesters.harvester.sgu.abstract import SguAPI, SkipProcessWell
from gwml2.harvesters.models.harvester import (
    HarvesterWellData, Harvester, HarvesterAttribute
)
from gwml2.models.general import Unit
from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.models.well import WellQualityMeasurement, Well
from gwml2.tasks.data_file_cache.country_recache import (
    generate_data_country_cache
)

LANSKOD_KEY = 'lanskod'
STATIONSID_KEY = 'stationsid'
LANSKOD_MAX_KEY = 'lanskod_max'


class SkipStationeer(Exception):
    """Raised stationeer done."""
    pass


class SguQualityAPI(SguAPI):
    """Harvester for
    https://www.sgu.se/grundvatten/miljoovervakning-av-grundvatten/kartvisare-och-diagram-for-miljoovervakning-av-grundvattenkemi/
    """

    def __init__(
            self, harvester: Harvester, replace: bool = False,
            original_id: str = None
    ):
        # Get previous lanskod
        attr, _ = HarvesterAttribute.objects.get_or_create(
            harvester=harvester,
            name=LANSKOD_MAX_KEY,
            defaults={'value': '26'}
        )
        self.lanskod_max = int(attr.value)
        super(SguQualityAPI, self).__init__(harvester, replace, original_id)

    def well_from_station(self, station: dict) -> HarvesterWellData:
        """Retrieves well data from station."""
        to_coord = SpatialReference(4326)
        from_coord = SpatialReference(self.crs)
        trans = CoordTransform(from_coord, to_coord)
        coordinates = station['geometry']['coordinates']

        point = Point(coordinates[0], coordinates[1], srid=self.crs)
        point.transform(trans)

        # check the station
        station_id = station['properties']['stationsid']
        name = station['properties']['stationsnamn']
        well, harvester_well_data = self._save_well(
            original_id=station_id,
            name=name,
            latitude=point.y,
            longitude=point.x,
        )
        return harvester_well_data

    def get_stations(self, lanskod: int) -> list[dict]:
        """Retrieves station data from Harvester.

        :return: Station data from Harvester and csr.
        :rtype: list, str
        """
        url = f"https://resource.sgu.se/oppnadata/grundvatten/api/miljoovervakning/stationer/{lanskod:02}?format=json"
        self._update('Fetching lanskod {}'.format(url))

        response = requests.get(url)
        if response.status_code == 404:
            raise SkipStationeer()
        data = response.json()
        self.crs = data['crs']['properties']['name']
        return data['features']

    def _process(self):
        """ Run the harvester """
        lanskod = 1
        previous_station = None

        # Get previous lanskod
        try:
            lanskod = int(
                HarvesterAttribute.objects.get(
                    harvester=self.harvester,
                    name=LANSKOD_KEY
                ).value
            )
        except (HarvesterAttribute.DoesNotExist, AttributeError):
            pass

        # Get previous station
        try:
            previous_station = HarvesterAttribute.objects.get(
                harvester=self.harvester,
                name=STATIONSID_KEY
            ).value
        except (HarvesterAttribute.DoesNotExist, AttributeError):
            pass

        while lanskod <= self.lanskod_max:
            try:
                try:
                    stations = self.get_stations(lanskod=lanskod)
                except requests.exceptions.JSONDecodeError:
                    raise SkipStationeer()

                total = len(stations)

                # ------------------------------------------
                # STATIONS
                # ------------------------------------------
                for well_idx, station in enumerate(stations):
                    # Resume previous one
                    stationsid = station['properties']['stationsid']
                    if previous_station and stationsid != previous_station:
                        continue
                    try:
                        harvester_well_data = self.well_from_station(station)
                        well = harvester_well_data.well
                    except (KeyError, TypeError, Well.DoesNotExist):
                        continue

                    # Save for last lanskod
                    previous_station = None
                    HarvesterAttribute.objects.update_or_create(
                        harvester=self.harvester,
                        name=STATIONSID_KEY,
                        defaults={
                            'value': stationsid,
                        }
                    )

                    try:
                        self.process_well(
                            harvester_well_data,
                            f'Saving lanskod {lanskod} - {well.original_id} :'
                            f' well({well_idx + 1}/{total})'
                        )
                    except SkipProcessWell:
                        pass
            except SkipStationeer:
                pass

            lanskod += 1
            # Save for last lanskod
            HarvesterAttribute.objects.update_or_create(
                harvester=self.harvester,
                name=LANSKOD_KEY,
                defaults={
                    'value': lanskod,
                }
            )
            try:
                HarvesterAttribute.objects.filter(
                    harvester=self.harvester
                ).filter(
                    name=STATIONSID_KEY
                ).delete()
            except HarvesterAttribute.DoesNotExist:
                pass

        # Delete the old one
        HarvesterAttribute.objects.filter(
            harvester=self.harvester
        ).filter(
            name__in=[LANSKOD_KEY, STATIONSID_KEY]
        ).delete()

        # Run country caches
        self._update('Run country caches')
        countries = list(set(self.countries))
        for country in countries:
            generate_data_country_cache(country)

    def process_well(
            self, harvester_well_data: HarvesterWellData, note: str
    ):
        """Processing well.
        """
        well = harvester_well_data.well
        response = self._request_api(
            f'https://resource.sgu.se/oppnadata/grundvatten/api/'
            f'miljoovervakning/station/{well.original_id}?format=json'
        )
        try:
            feature = response['features'][0]
        except IndexError:
            raise SkipProcessWell()

        properties = feature['properties']
        original_id = properties['stationsid']

        # Skip if it does not return the same station id
        if well.original_id != original_id:
            raise SkipProcessWell()

        self._update(note)

        # Measurement total
        updated = False

        for measurement_property in properties['provtagningar']:
            date_time = make_aware(
                parser.parse(measurement_property['provtagningsdatum'])
            )
            measurements = measurement_property['parametrar']
            for measurement in measurements:
                try:
                    parameter = TermMeasurementParameter.objects.get(
                        name__iexact=measurement['paramnamn_kort']
                    )
                    value = measurement['matvardetal']
                    unit = Unit.objects.get(
                        name__iexact=measurement['enhet']
                    )
                    last = well.wellqualitymeasurement_set.filter(
                        parameter=parameter
                    ).order_by('-time').first()
                    if last and date_time <= last.time:
                        continue

                    self._update(
                        f'{note}'
                        f'measurement: {parameter.name}'
                    )
                    self._save_measurement(
                        model=WellQualityMeasurement,
                        time=date_time,
                        defaults={
                            'parameter': parameter
                        },
                        harvester_well_data=harvester_well_data,
                        value=value,
                        unit=unit
                    )
                    updated = True
                except (
                        TermMeasurementParameter.DoesNotExist,
                        Unit.DoesNotExist, KeyError
                ):
                    continue
        if updated:
            self.well_updated(well=well)
