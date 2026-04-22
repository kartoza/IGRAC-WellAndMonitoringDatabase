import re

import requests
from dateutil import parser
from django.contrib.gis.geos import Point

from core.utils import deepl_translater
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

    def get_original_id(self, station: dict) -> str:
        """Retrieves original id from station."""
        return station['properties']['id']

    def well_from_station(self, station: dict) -> HarvesterWellData:
        """Retrieves well data from station."""
        coordinates = station['geometry']['coordinates']

        point = Point(coordinates[0], coordinates[1], srid=4326)

        # check the station
        station_id = self.get_original_id(station)
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
            self._update(
                f'Processing : {well_idx + 1}/{total}'
            )

            try:
                try:
                    self.process_station(
                        station,
                        well_idx=well_idx,
                        total=total,
                    )
                except SkipProcessWell:
                    pass
            except (KeyError, TypeError, Well.DoesNotExist) as e:
                print(f"{e}")
                continue

        # Run country caches
        self._update('Run country caches')
        countries = list(set(self.countries))
        for country in countries:
            generate_data_country_cache(country)

    def process_well(self, harvester_well_data: HarvesterWellData, note: str):
        """Processing well."""
        pass

    def get_estimated_flow(self, station: dict) -> str | None:
        """Fetch estimated flow text from SGU WMS GetFeatureInfo.

        Uses the station's projected coordinates (n/e in EPSG:3006) to build
        a 21×21 pixel bounding box centred on the point, then extracts the
        'Flöde' property.
        """
        props = station['properties']
        n = props.get('n')
        e = props.get('e')
        if not n or not e:
            return None

        bbox = f"{e - 10},{n - 10},{e + 10},{n + 10}"
        url = (
            "https://maps3.sgu.se/geoserver/wms"
            "?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetFeatureInfo"
            "&LAYERS=grundvatten:SE.GOV.SGU.KALLOR.1M"
            "&QUERY_LAYERS=grundvatten:SE.GOV.SGU.KALLOR.1M"
            "&INFO_FORMAT=application/json&FEATURE_COUNT=5"
            f"&SRS=EPSG:3006&WIDTH=21&HEIGHT=21&X=10&Y=10&BBOX={bbox}"
        )
        station_id = props.get('id')
        try:
            response = requests.get(url, timeout=10)
            features = response.json().get('features', [])
            if not features:
                return None
            feature = next(
                (f for f in features
                 if f['properties'].get('Id') == station_id),
                None
            )
            if not feature:
                return None
            estimated_flow = feature['properties'].get('Flöde')
            if estimated_flow and not re.search(r'\d', estimated_flow):
                return None
            return estimated_flow
        except Exception:
            return None

    def process_station(
            self,
            station,
            well_idx: int = None,
            total: int = None,
    ):
        """Processing station."""
        original_id = self.get_original_id(station)

        self.check_current_well(original_id)
        if not self.is_processing_station:
            raise SkipProcessWell()

        self._update(
            f'Saving {original_id} :'
            f' well({well_idx + 1}/{total})'
        )
        # Estimated flow — prefer WMS detail over the OGC summary field
        estimated_flow = (
                self.get_estimated_flow(station)
                or station['properties'].get('fl_txt')
        )

        harvester_well_data = self.well_from_station(station)
        well = harvester_well_data.well

        if well:
            # Description
            description = station['properties']['notering']
            if not well.description:
                well.description = description

            # Remove link
            if description and re.search(
                r'<a\b[^>]*>.*?</a>', description,
                flags=re.IGNORECASE | re.DOTALL
            ):
                description = re.sub(
                    r'<a\b[^>]*>.*?</a>', '', description,
                    flags=re.IGNORECASE | re.DOTALL
                ).strip()
                well.description = description

            if description:
                if well.description == description:
                    # We translate this to english
                    try:
                        well.description = deepl_translater(description)
                    except Exception as e:
                        well.description = description

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

            # If empty, add estimated flow
            if not well.estimated_flow:
                well.estimated_flow = estimated_flow

            # If estimated flow is empty, update it
            if not estimated_flow:
                well.estimated_flow = estimated_flow

            # If estimated flow is not empty, and the well and input same
            # do translation
            if estimated_flow and well.estimated_flow == estimated_flow:
                try:
                    well.estimated_flow = deepl_translater(estimated_flow)
                except Exception:
                    well.estimated_flow = estimated_flow
            well.save()

        # Measurements
        updated = False
        date_time = parser.parse(station['properties']['obsdat'])
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
