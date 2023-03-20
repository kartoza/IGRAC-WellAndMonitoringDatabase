import json

import requests
from bs4 import BeautifulSoup
from dateutil import parser
from django.utils.timezone import make_aware

from gwml2.harvesters.harvester.base import BaseHarvester
from gwml2.harvesters.models.harvester import Harvester
from gwml2.models.general import Quantity, Unit
from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.models.well import (
    Well, HydrogeologyParameter, Management, WellLevelMeasurement,
    MEASUREMENT_PARAMETER_GROUND
)


class AzulBdh(BaseHarvester):
    """
    Harvester for http://www.azul.bdh.org.ar/bdh3/leaflet/index.html
    """

    def __init__(
            self, harvester: Harvester, replace: bool = False,
            original_id: str = None
    ):
        # Website need session before able to access other website
        self.request = requests.Session()
        self.request.get('http://www.azul.bdh.org.ar/bdh3/index_contenido.php')

        self.unit_m = Unit.objects.get(name='m')
        self.parameter = TermMeasurementParameter.objects.get(
            name=MEASUREMENT_PARAMETER_GROUND)
        super(AzulBdh, self).__init__(harvester, replace, original_id)

    def _process(self):
        """ Run the harvester """

        # Fetch Stations
        stations_url = (
            'http://www.azul.bdh.org.ar/bdh3/leaflet/datos/estaciones.js'
        )
        response = self.request.get(stations_url)
        self._update('Fetching stations {}'.format(stations_url))

        if response.status_code != 200:
            raise Exception(f"Error : {response.text}")

        # We get the level stations
        stations = str(response.content).split(
            'var gjson_estaciones_well = ')[1].split(
            'var gjson_estaciones_sm = ')[0]
        stations = stations.split('"features": [')
        stations[0] = stations[0].replace(
            '\\n', '').replace("/*", '').replace("*/", '')
        stations[1] = stations[1].replace(
            '"', '').replace('\\n', '').replace("\\'", '"').replace('\\xc3\\',
                                                                    "")

        # Clean stations from unneeded character
        clean_station = '"features": ['.join(stations)
        stations = ' '.join(clean_station.split()).replace(
            ', }', '}').replace(', ]};', ']}')
        stations = json.loads(stations)

        # Fetch detail all station
        well_total = len(stations['features'])
        for well_idx, station in enumerate(stations['features']):
            self._update(
                'Saving : well({}/{})'.format(well_idx + 1, well_total)
            )
            self.get_station_data(station)

    def get_station_data(self, station):
        """ Get station data.

        Mostly for fetching detail and also level data"""
        properties = station['properties']
        station_url = (
            f'http://www.azul.bdh.org.ar/bdh3/{properties["pagina"]}?'
            f'idpoint={properties["id"]}&xgap_historial=clear'
        )
        response = self.request.get(station_url)

        if response.status_code != 200:
            raise Exception(f"Error : {response.text}")

        soup = BeautifulSoup(response.content)
        table = soup.find("table", {"id": "table"})
        details = {}
        for row in table.findAll('tr'):
            columns = row.findAll('td')
            if len(columns) >= 2:
                key = columns[0].text.replace('\n', '')
                value = columns[1].text.replace('\n', '')
                if key == 'Nombre':
                    details['name'] = value
                    details['original_id'] = value
                elif key == 'Latitud':
                    details['latitude'] = float(value)
                elif key == 'Longitud':
                    details['longitude'] = float(value)
                elif key == 'Cota de terreno [m]':
                    try:
                        details['ground_surface_elevation_masl'] = float(value)
                    except ValueError:
                        details['ground_surface_elevation_masl'] = None
                elif key == 'Cota de boca de pozo [m]':
                    try:
                        details['top_of_well_elevation_masl'] = float(value)
                    except ValueError:
                        details['top_of_well_elevation_masl'] = None
                elif key == 'Acuífero':
                    details['aquifer'] = value.replace('\xa0', '')
                elif key == 'Propietario/Responsable':
                    details['owner'] = value
        try:
            # Save well
            well, harvester_well_data = self._save_well(
                original_id=details['name'],
                name=details['name'],
                latitude=details['latitude'],
                longitude=details['longitude'],
                ground_surface_elevation_masl=details[
                    'ground_surface_elevation_masl'],
                top_of_well_elevation_masl=details[
                    'top_of_well_elevation_masl']
            )
            if details['aquifer']:
                hydrogeology_parameter = well.hydrogeology_parameter
                if not well.hydrogeology_parameter:
                    hydrogeology_parameter = HydrogeologyParameter()
                hydrogeology_parameter.aquifer_name = details['aquifer']
                hydrogeology_parameter.save()
                well.hydrogeology_parameter = hydrogeology_parameter
                well.save()

            if details['owner']:
                management = well.management
                if not well.management:
                    management = Management()
                management.manager = details['owner']
                management.save()
                well.management = management
                well.save()

            measurements_url = (
                f'http://www.azul.bdh.org.ar/bdh3/nivel_listado.php?'
                f'idpoint={properties["id"]}&'
                f'xgap_param_idpoint={properties["id"]}&'
                f'retorno={properties["pagina"]}'
            )
            self.measurements(harvester_well_data, measurements_url)
        except Well.DoesNotExist:
            pass

    def measurements(self, harvester_well_data, url: str):
        """ Return measurement of station."""
        response = self.request.get(url)
        self._update('Saving measurements {}'.format(url))

        measurements = []
        if response.status_code == 200:
            soup = BeautifulSoup(response.content)
            table = soup.find("tbody", {"id": "BodyListado"})
            for row in table.findAll('tr'):
                try:
                    date = row.findAll('td')[0].text.replace('\n', '')
                    value = row.findAll('td')[2].text.replace('\n', '')
                    value = float(value)
                    date_time = make_aware(parser.parse(date))
                    defaults = {
                        'parameter': self.parameter
                    }
                    self._save_measurement(
                        WellLevelMeasurement,
                        date_time,
                        defaults,
                        harvester_well_data,
                        value,
                        self.unit_m
                    )
                except (ValueError, IndexError):
                    pass
        return measurements
