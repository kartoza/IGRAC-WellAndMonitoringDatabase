import requests
from dateutil import parser
from django.contrib.gis.geos import Point

from gwml2.harvesters.harvester.sgu.abstract import SguAPI, SkipProcessWell
from gwml2.harvesters.models.harvester import (
    HarvesterWellData, Harvester, HarvesterParameterMap
)
from gwml2.models.term_measurement_parameter import (
    TermMeasurementParameterGroup
)
from gwml2.models.well import Well, HydrogeologyParameter
from gwml2.tasks.data_file_cache.country_recache import (
    generate_data_country_cache
)

LANSKOD_KEY = 'lanskod'
STATIONSID_KEY = 'stationsid'
LANSKOD_MAX_KEY = 'lanskod_max'


class SkipStationeer(Exception):
    """Raised stationeer done."""
    pass


class SguSpringAPI(SguAPI):
    """Harvester for
    https://apps.sgu.se/kartvisare/kartvisare-kallor.html
    """

    def __init__(
            self, harvester: Harvester, replace: bool = False,
            original_id: str = None
    ):
        self.parameters = HarvesterParameterMap.get_json(harvester)
        super(SguSpringAPI, self).__init__(harvester, replace, original_id)

    def well_from_station(self, station: dict) -> HarvesterWellData:
        """Retrieves well data from station."""
        coordinates = station['geometry']['coordinates']

        point = Point(coordinates[0], coordinates[1], srid=4326)

        # check the station
        station_id = station['properties']['id']
        name = station['properties']['namn']
        well, harvester_well_data = self._save_well(
            original_id=station_id,
            name=name,
            latitude=point.y,
            longitude=point.x,
        )
        if well.feature_type != self.harvester.feature_type:
            well.feature_type = self.harvester.feature_type
            well.save()
        return harvester_well_data

    def _process(self):
        """ Run the harvester """
        url = f"https://api.sgu.se/oppnadata/kallor/ogc/features/v1/collections/kallor/items?f=application%2Fvnd.ogc.fg%2Bjson"
        self._update('Fetching data')
        response = requests.get(url)
        stations = response.json()['features']
        total = len(stations)

        for well_idx, station in enumerate(stations):
            # Resume previous one
            try:
                harvester_well_data = self.well_from_station(station)
                well = harvester_well_data.well

                # Aquifer name
                aquifer_name = station['properties']['akvtyp_txt']
                if aquifer_name:
                    hydrogeology_parameter = well.hydrogeology_parameter
                    if not well.hydrogeology_parameter:
                        hydrogeology_parameter = HydrogeologyParameter()
                    hydrogeology_parameter.aquifer_name = aquifer_name
                    hydrogeology_parameter.save()
                    well.hydrogeology_parameter = hydrogeology_parameter
                    well.save()

                # Estimated flow
                estimated_flow = station['properties']['fl_txt']
                well.estimated_flow = estimated_flow
                well.save()

                try:
                    self.process_station(
                        station, harvester_well_data,
                        (
                            f'Saving {well.original_id} :'
                            f' well({well_idx + 1}/{total})'
                        )
                    )
                except SkipProcessWell:
                    pass
            except (KeyError, TypeError, Well.DoesNotExist) as e:
                continue

        # Run country caches
        self._update('Run country caches')
        countries = list(set(self.countries))
        for country in countries:
            generate_data_country_cache(country)

    def process_well(self, harvester_well_data: HarvesterWellData, note: str):
        """Processing well."""
        pass

    def process_station(
            self,
            station,
            harvester_well_data: HarvesterWellData,
            note
    ):
        """Processing station."""
        well = harvester_well_data.well
        date_time = parser.parse(station['properties']['obsdat'])
        updated = False
        self._update(note)

        for key, _parameter in self.parameters.items():
            try:
                value = station['properties'][key]
                parameter = _parameter['parameter']
                unit = _parameter['unit']
                if value and parameter:
                    if isinstance(value, str):
                        value = value.replace(',', '.')

                    MeasurementModel = (
                        TermMeasurementParameterGroup.get_measurement_model(
                            parameter
                        )
                    )
                    self._save_measurement(
                        model=MeasurementModel,
                        time=date_time,
                        defaults={
                            'parameter': parameter
                        },
                        harvester_well_data=harvester_well_data,
                        value=value,
                        unit=unit
                    )
                    updated = True
            except KeyError:
                pass

        if updated:
            self.well_updated(well=well)
