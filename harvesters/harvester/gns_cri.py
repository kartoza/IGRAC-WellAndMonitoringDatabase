"""Harvester of using data.gns.cri.nz : New Zealand"""
import csv
import io
from datetime import datetime

import requests
from django.utils.timezone import make_aware

from gwml2.harvesters.harvester.base import BaseHarvester
from gwml2.harvesters.models.harvester import Harvester
from gwml2.models.general import Unit
from gwml2.models.management import Management
from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.models.well import Well, WellQualityMeasurement


class GnsCri(BaseHarvester):
    """
    Harvester for https://data.gns.cri.nz/gwp/index.html?map=NGMP
    """

    def __init__(
            self, harvester: Harvester, replace: bool = False,
            original_id: str = None
    ):
        self.parameters = {
            'Acidity pH units': {
                'model': WellQualityMeasurement,
                'parameter': TermMeasurementParameter.objects.get(name='pH')
            },
            'Bicarbonate mg/L as HCO3 - total': {
                'model': WellQualityMeasurement,
                'parameter': TermMeasurementParameter.objects.get(name='HCO₃')
            },
            'Calcium mg/L - All Forms as Ca - filterable': {
                'model': WellQualityMeasurement,
                'parameter': TermMeasurementParameter.objects.get(name='Ca')
            },
            'Chloride mg/L as Cl - filterable': {
                'model': WellQualityMeasurement,
                'parameter': TermMeasurementParameter.objects.get(name='Cl')
            },
            'Fluorine mg/L (fluoride) as F - filterable': {
                'model': WellQualityMeasurement,
                'parameter': TermMeasurementParameter.objects.get(name='F')
            },
            'Iron mg/L All forms as Fe - filterable': {
                'model': WellQualityMeasurement,
                'parameter': TermMeasurementParameter.objects.get(name='Fe')
            },
            'Magnesium mg/L - All Forms as Mg - filterable': {
                'model': WellQualityMeasurement,
                'parameter': TermMeasurementParameter.objects.get(name='Mg')
            },
            'Manganese mg/L All forms as Mn - filterable': {
                'model': WellQualityMeasurement,
                'parameter': TermMeasurementParameter.objects.get(name='Mn')
            },
            'Phosphorus mg/L as P- Reactive - filterable': {
                'model': WellQualityMeasurement,
                'parameter': TermMeasurementParameter.objects.get(name='P')
            },
            'Potassium mg/L - All Forms as K -filterable': {
                'model': WellQualityMeasurement,
                'parameter': TermMeasurementParameter.objects.get(name='K')
            },
            'Sodium mg/L - All Forms as Na - filterable': {
                'model': WellQualityMeasurement,
                'parameter': TermMeasurementParameter.objects.get(name='Na')
            },
            'Sulphate mg/L as SO4 - filterable': {
                'model': WellQualityMeasurement,
                'parameter': TermMeasurementParameter.objects.get(name='SO₄')
            },
            'Temperature Deg. C': {
                'model': WellQualityMeasurement,
                'parameter': TermMeasurementParameter.objects.get(name='T')
            },
            'Temperature Deg. C- analysis temperature': {
                'model': WellQualityMeasurement,
                'parameter': TermMeasurementParameter.objects.get(name='T')
            },
            'Total solids (electrical conductivity) uS/cm at 25 degrees': {
                'model': WellQualityMeasurement,
                'parameter': TermMeasurementParameter.objects.get(name='EC')
            },
        }
        super(GnsCri, self).__init__(harvester, replace, original_id)

    def _process(self):
        # fetch stations first
        domain = 'https://data.gns.cri.nz'
        url = (
            f'{domain}/mapservice/api/1.0/jsmap/proxy?'
            f'url=https%3A%2F%2Fdata.gns.cri.nz%2Fwebmaps%2Fgns%2Fggw%2Fwfs'
            f'&maxFeatures=1000&outputFormat=application%2Fjson'
            f'&propertyName=feature_public_id,feature,Name,Description,'
            f'Feature_comments,country,Location_description,Feature_type,'
            f'Project,Regional_authority,geometry'
            f'&request=GetFeature&service=wfs&srsName=EPSG:4326&version=1.1.0'
            f'&typeNames=ggw:NationalGroundwaterMonitoringProgramme'
        )
        stations = self._request_api(url)
        count = len(stations['features'])
        for idx, station in enumerate(stations['features']):
            properties = station['properties']
            original_id = properties['feature']
            self._update(f'Processing {original_id} - {idx}/{count}')
            self._process_measurement(station)

        self._done('Done')

    def _process_measurement(self, station):
        """Process measurement of station."""
        properties = station['properties']
        original_id = properties['feature']
        name = properties['Name']
        description = properties['Description']
        manager = properties['Regional_authority']
        latitude = station['geometry']['coordinates'][1]
        longitude = station['geometry']['coordinates'][0]
        domain = 'https://ggw.gns.cri.nz'
        csv_url = (
            f'{domain}/ggwdata/export/exportDetailedAnalysisResults.csv?'
            f'FEATURE={original_id}'
        )
        response = requests.get(csv_url)
        harvester_well_data = None
        if response.status_code == 200:
            # Parse the measurements
            buff = io.StringIO(response.text)
            data = csv.DictReader(buff)
            for row in data:
                try:
                    # Just save well if there are measurements
                    if not harvester_well_data:
                        # -----------------------------------
                        # Save the well
                        try:
                            well, harvester_well_data = self._save_well(
                                original_id,
                                name,
                                latitude=latitude,
                                longitude=longitude
                            )
                        except Well.DoesNotExist:
                            return

                        # Save management
                        if not well.management:
                            management = Management.objects.create(
                                manager=manager)
                            well.management = management

                        well.description = description
                        well.save()

                    param_type = row['Param Type']
                    param = self.parameters[param_type]
                    date_time = make_aware(
                        datetime.strptime(
                            row['Sample Date NZST'], '%Y-%m-%d %H:%M:%S'
                        )
                    )
                    value = float(row['Analysis Result'])
                    unit_name = row['Result Param Units']

                    if unit_name == 'Deg. C':
                        unit_name = '°C'
                    if unit_name == 'uS/cm':
                        unit_name = 'μS/cm'

                    unit = None
                    if unit_name != 'pH':
                        unit = Unit.objects.get(name=unit_name)
                    defaults = {
                        'parameter': param['parameter'],
                        'methodology': row['Param Method']
                    }
                    self._save_measurement(
                        param['model'],
                        date_time,
                        defaults,
                        harvester_well_data,
                        value,
                        unit
                    )
                except (KeyError, TypeError, ValueError, Unit.DoesNotExist):
                    pass

        if harvester_well_data:
            self.post_processing_well(harvester_well_data.well)
