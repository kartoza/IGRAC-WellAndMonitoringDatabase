"""Harvester of using hubeau."""

from datetime import datetime, timezone, timedelta

import requests
from django.contrib.gis.geos import Point

from gwml2.harvesters.harvester.base import BaseHarvester
from gwml2.harvesters.models import Harvester, HarvesterParameterMap
from gwml2.harvesters.models.harvester import (
    HarvesterAttribute,
    HarvesterWellData
)
from gwml2.models import (
    Unit, TermMeasurementParameter, MEASUREMENT_PARAMETER_AMSL
)
from gwml2.models.well import (
    Well, WellLevelMeasurement, WellQualityMeasurement
)
from gwml2.tasks.data_file_cache.country_recache import (
    generate_data_country_cache
)


class KeskkonnaportaalEstoniaHarvester(BaseHarvester):
    """Keskkonnaportaal harvester."""

    countries = []

    def __init__(
            self, harvester: Harvester, replace: bool = False,
            original_id: str = None
    ):
        self.level_parameter = TermMeasurementParameter.objects.get(
            name=MEASUREMENT_PARAMETER_AMSL
        )
        self.parameters = HarvesterParameterMap.get_json(harvester)
        station_attr, _ = HarvesterAttribute.objects.get_or_create(
            harvester=harvester,
            name='station_url',
            defaults={
                'value': 'https://gsavalik7.envir.ee/geoserver/eelis/ows?SERVICE=WFS&VERSION=1.1.0&REQUEST=GetFeature&TYPENAME=eelis:kr_puurkaev&OUTPUTFORMAT=application/json&SRSNAME=EPSG:4326'
            }
        )
        self.station_url = station_attr.value
        station_detail_attr, _ = HarvesterAttribute.objects.get_or_create(
            harvester=harvester,
            name='station_detail_url',
            defaults={
                'value': 'https://register.keskkonnaportaal.ee/services/kkr/driven-well/services/driven-well-details'
            }
        )
        self.station_detail_url = station_detail_attr.value

        prefix_name, _ = HarvesterAttribute.objects.get_or_create(
            harvester=harvester,
            name='prefix_name',
            defaults={
                'value': 'EE00_'
            }
        )
        self.prefix_name = prefix_name.value

        super(KeskkonnaportaalEstoniaHarvester, self).__init__(
            harvester, replace, original_id
        )

    def well_updated(self, well: Well):
        """When the well is updated."""
        self.post_processing_well(
            well, generate_country_cache=False
        )
        self.countries.append(well.country.code)

    def well_from_station(self, station: dict) -> HarvesterWellData:
        """Retrieves well data from station."""
        coordinates = station['geometry']['coordinates']

        point = Point(coordinates[0], coordinates[1], srid=4326)

        # check the station
        station_id = f"{self.prefix_name}{station['properties']['kr_kood']}"
        name = station_id
        well, harvester_well_data = self._save_well(
            original_id=station_id,
            name=name,
            latitude=point.y,
            longitude=point.x,
        )
        return harvester_well_data

    def _process(self):
        """ Run the harvester """
        self._update('Fetching stations')
        response = requests.get(self.station_url)
        stations = response.json()['features']
        total = len(stations)

        for well_idx, station in enumerate(stations):
            # Resume previous one
            try:
                harvester_well_data = self.well_from_station(station)
                well = harvester_well_data.well
                if not self.is_processing_station:
                    continue

                self._update(
                    f'Saving {well.original_id} : well({well_idx + 1}/{total})'
                )
                self.process_station(harvester_well_data)
            except (KeyError, TypeError, Well.DoesNotExist) as e:
                continue

        # Run country caches
        self._update('Run country caches')
        countries = list(set(self.countries))
        for country in countries:
            generate_data_country_cache(country)

    def process_level_measurement(
            self,
            harvester_well_data: HarvesterWellData
    ):
        """Processing level measurement."""
        well = harvester_well_data.well
        # ----------------------------------------------
        # Level measurement
        # ----------------------------------------------
        monitoring = harvester_well_data.well.name.replace(
            self.prefix_name, ''
        )
        data = [
            ("filter.stations", monitoring),
            ("filter.parameters", "n100002706"),
            ("filter.programFilter.names", "Põhjavee seire"),
            ("filter.programFilter.names", "Põhjaveekogumite seire"),
            (
                "filter.programFilter.names",
                "Nitraaditundliku ala põhjavee seire"
            ),
            (
                "filter.programFilter.names",
                "Kirde-Eesti tööstuspiirkonna põhjav. org. ühendid"
            ),
            (
                "filter.programFilter.names",
                "Kirde-Eesti tööstuspiirkonna põhjavee seire"
            ),
            ("filter.programFilter.names", "Põhjaveekogumite keemiline seire"),
            (
                "filter.programFilter.names",
                "Põhjaveekogumite koguseline seire"
            ),
        ]
        last_measurement = well.welllevelmeasurement_set.order_by(
            '-time').first()
        if last_measurement:
            next_day = last_measurement.time + timedelta(days=1)
            data.append(
                (
                    "filter.monitoringDateStart",
                    next_day.strftime("%d.%m.%Y")
                )
            )

        session = requests.Session()
        session.get("https://kese.envir.ee/kese/")
        response = session.post(
            "https://kese.envir.ee/kese/fetchParameterValueNew.action",
            data=data
        )

        response_json = response.json()
        if len(response_json['data']):
            for measurement in response_json['data']:
                value_with_unit = measurement['convertedValueWithUnit']
                if value_with_unit:
                    value_str, unit = value_with_unit.replace(",", ".").split()
                    try:
                        value = float(value_str)
                    except ValueError:
                        continue
                    time = datetime.strptime(
                        measurement["formattedMonitoringTime"],
                        "%d.%m.%Y %H:%M"
                    ).replace(tzinfo=timezone.utc)
                    try:
                        unit = Unit.objects.get(name=unit)
                        defaults = {
                            'parameter': self.level_parameter,
                        }
                        self._save_measurement(
                            WellLevelMeasurement,
                            time,
                            defaults,
                            harvester_well_data,
                            value,
                            unit
                        )
                    except Unit.DoesNotExist:
                        pass
            self.process_level_measurement(harvester_well_data)

    def process_quantity_measurement(
            self,
            harvester_well_data: HarvesterWellData
    ):
        """Processing quantity measurement."""
        # ----------------------------------------------
        # Quality measurement and detail
        # ----------------------------------------------
        kood = harvester_well_data.well.original_id.replace(
            self.prefix_name, ''
        )
        response = requests.post(
            self.station_detail_url, json={"kood": kood}
        )
        for measurement in response.json()['akt']:
            time = datetime.fromisoformat(
                measurement['kp']
            ).replace(tzinfo=timezone.utc)
            for analysis in measurement['analyys']:
                try:
                    param = self.parameters[analysis['param']]
                    value = float(analysis['vaartus'])
                    unit = None
                    if analysis['yhik']:
                        unit = Unit.objects.get(name__iexact=analysis['yhik'])
                    defaults = {
                        'parameter': param['parameter'],
                    }
                    self._save_measurement(
                        WellQualityMeasurement,
                        time,
                        defaults,
                        harvester_well_data,
                        value,
                        unit
                    )
                except (ValueError, KeyError, Unit.DoesNotExist):
                    pass

    def process_station(
            self,
            harvester_well_data: HarvesterWellData
    ):
        """Processing station."""
        well = harvester_well_data.well
        self.process_level_measurement(harvester_well_data)
        self.process_quantity_measurement(harvester_well_data)

        print(f'{well.original_id} : done')
        # -----------------------
        # Generate cache
        if well:
            self.post_processing_well(
                well, generate_country_cache=False
            )
            if well.country:
                self.countries.append(well.country.code)
