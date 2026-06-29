"""Tests for GenerateWellCacheFile — full integration with all generators."""
import json
import os
import shutil

from django.contrib.gis.geos import Point

from gwml2.models.construction import Construction, ConstructionStructure
from gwml2.models.drilling import Drilling, StratigraphicLog, WaterStrike
from gwml2.models.general import Quantity
from gwml2.models.geology import Geology
from gwml2.models.hydrogeology import HydrogeologyParameter
from gwml2.models.management import Management
from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.tasks.well_file_cache.wells_cache import (
    GENERATORS, GenerateWellCacheFile
)
from gwml2.tests.base import GWML2Test
from gwml2.tests.model_factories import (
    WellF,
    WellLevelMeasurementF,
    WellQualityMeasurementF,
    WellYieldMeasurementF,
)
from gwml2.utils.ods_reader import extract_data, get_count


def run_cache_generator(well, generators=None):
    GenerateWellCacheFile(well, force_regenerate=True, generators=generators)


def load_data_json(well):
    with open(os.path.join(well.data_cache_folder, 'data.json')) as f:
        return json.load(f)


def monitoring_ods_path(well):
    return os.path.join(well.data_cache_folder, 'monitoring_data.ods')


def read_ods_rows(well, sheet_name):
    rows = []
    extract_data(monitoring_ods_path(well), sheet_name, rows.append)
    return rows


class GenerateWellCacheFileTest(GWML2Test):
    """Integration tests covering all generators."""

    def setUp(self):
        self.measurement_parameter = TermMeasurementParameter.objects.create(
            name='Water depth'
        )

        self.well = WellF(
            original_id='TEST001',
            name='Test Well',
            description='Integration test well',
            location=Point(106.8, -6.2),
        )

        # Hydrogeology
        hydrogeology = HydrogeologyParameter.objects.create(
            aquifer_name='Test Aquifer',
            aquifer_material='Sandstone',
            aquifer_thickness='10',
            degree_of_confinement=0.8,
        )
        self.well.hydrogeology_parameter = hydrogeology

        # Management
        management = Management.objects.create(number_of_users=25)
        self.well.management = management

        # Geology
        total_depth_quantity = Quantity.objects.create(value=120.0)
        geology = Geology.objects.create(total_depth=total_depth_quantity)
        self.well.geology = geology

        # Drilling
        drilling = Drilling.objects.create(
            driller='Test Driller Co.',
            year_of_drilling=2018,
            successful=True,
        )
        self.well.drilling = drilling

        # Construction
        construction = Construction.objects.create(
            pump_installer='Pump Co.',
            pump_description='Submersible pump',
        )
        self.well.construction = construction

        self.well.save()

        # Sub-items linked to drilling
        WaterStrike.objects.create(
            drilling=drilling,
            depth=Quantity.objects.create(value=35.0),
            description='First water strike',
        )
        StratigraphicLog.objects.create(
            drilling=drilling,
            top_depth=Quantity.objects.create(value=0.0),
            bottom_depth=Quantity.objects.create(value=20.0),
            material='Clay',
        )

        # Sub-items linked to construction
        ConstructionStructure.objects.create(
            construction=construction,
            material='Steel',
            description='Casing',
            top_depth=Quantity.objects.create(value=0.0),
            bottom_depth=Quantity.objects.create(value=50.0),
        )

        # Measurements
        self.level_measurement_1 = WellLevelMeasurementF(
            well=self.well, parameter=self.measurement_parameter
        )
        self.level_measurement_2 = WellLevelMeasurementF(
            well=self.well, parameter=self.measurement_parameter
        )
        self.quality_measurement = WellQualityMeasurementF(
            well=self.well, parameter=self.measurement_parameter
        )
        self.yield_measurement = WellYieldMeasurementF(
            well=self.well, parameter=self.measurement_parameter
        )

    def tearDown(self):
        cache_folder = self.well.data_cache_folder
        if os.path.exists(cache_folder):
            shutil.rmtree(cache_folder)

    # ------------------------------------------------------------------
    # data.json structure
    # ------------------------------------------------------------------

    def test_data_json_created(self):
        run_cache_generator(
            self.well, [GENERATORS.GENERAL_INFORMATION]
        )
        data_json_path = os.path.join(self.well.data_cache_folder, 'data.json')
        self.assertTrue(os.path.exists(data_json_path))

    def test_all_json_keys_present(self):
        run_cache_generator(self.well, [
            GENERATORS.GENERAL_INFORMATION,
            GENERATORS.HYDROGEOLOGY,
            GENERATORS.MANAGEMENT,
            GENERATORS.DRILLING_AND_CONSTRUCTION,
        ])
        cache_data = load_data_json(self.well)
        for expected_key in (
                'General Information', 'Hydrogeology', 'Management', 'Drilling'
        ):
            with self.subTest(key=expected_key):
                self.assertIn(expected_key, cache_data)

    # ------------------------------------------------------------------
    # General Information
    # ------------------------------------------------------------------

    def test_general_information_original_id_and_name(self):
        run_cache_generator(self.well, [GENERATORS.GENERAL_INFORMATION])
        general_info_row = load_data_json(self.well)['General Information'][0]
        self.assertEqual(general_info_row[0], 'TEST001')
        self.assertEqual(general_info_row[1], 'Test Well')

    def test_general_information_location(self):
        run_cache_generator(self.well, [GENERATORS.GENERAL_INFORMATION])
        general_info_row = load_data_json(self.well)['General Information'][0]
        self.assertAlmostEqual(general_info_row[7], -6.2, places=5)
        self.assertAlmostEqual(general_info_row[8], 106.8, places=5)

    def test_general_information_description(self):
        run_cache_generator(self.well, [GENERATORS.GENERAL_INFORMATION])
        general_info_row = load_data_json(self.well)['General Information'][0]
        self.assertEqual(general_info_row[6], 'Integration test well')

    # ------------------------------------------------------------------
    # Hydrogeology
    # ------------------------------------------------------------------

    def test_hydrogeology_aquifer_fields(self):
        run_cache_generator(self.well, [GENERATORS.HYDROGEOLOGY])
        hydrogeology_row = load_data_json(self.well)['Hydrogeology'][0]
        self.assertEqual(hydrogeology_row[0], 'TEST001')
        self.assertEqual(hydrogeology_row[2], 'Test Aquifer')
        self.assertEqual(hydrogeology_row[3], 'Sandstone')

    # ------------------------------------------------------------------
    # Management
    # ------------------------------------------------------------------

    def test_management_number_of_users(self):
        run_cache_generator(self.well, [GENERATORS.MANAGEMENT])
        management_row = load_data_json(self.well)['Management'][0]
        self.assertEqual(management_row[0], 'TEST001')
        self.assertEqual(management_row[3], 25)

    # ------------------------------------------------------------------
    # Drilling & Construction
    # ------------------------------------------------------------------

    def test_drilling_basic_fields(self):
        run_cache_generator(self.well, [GENERATORS.DRILLING_AND_CONSTRUCTION])
        drilling_row = load_data_json(self.well)['Drilling'][0]
        self.assertEqual(drilling_row[0], 'TEST001')
        self.assertEqual(drilling_row[5], 'Test Driller Co.')
        self.assertEqual(drilling_row[8], 2018)

    def test_drilling_total_depth(self):
        run_cache_generator(self.well, [GENERATORS.DRILLING_AND_CONSTRUCTION])
        drilling_row = load_data_json(self.well)['Drilling'][0]
        self.assertEqual(drilling_row[2], 120.0)

    def test_water_strike_written(self):
        run_cache_generator(self.well, [GENERATORS.DRILLING_AND_CONSTRUCTION])
        water_strike_rows = load_data_json(self.well).get('Water Strike', [])
        self.assertEqual(len(water_strike_rows), 1)
        self.assertEqual(water_strike_rows[0][2], 35.0)

    def test_stratigraphic_log_written(self):
        run_cache_generator(self.well, [GENERATORS.DRILLING_AND_CONSTRUCTION])
        stratigraphic_rows = load_data_json(self.well).get('Stratigraphic Log',
                                                           [])
        self.assertEqual(len(stratigraphic_rows), 1)
        self.assertEqual(stratigraphic_rows[0][7], 'Clay')

    def test_construction_structure_written(self):
        run_cache_generator(self.well, [GENERATORS.DRILLING_AND_CONSTRUCTION])
        construction_rows = load_data_json(self.well).get('Construction', [])
        self.assertEqual(len(construction_rows), 1)
        self.assertEqual(construction_rows[0][10], 'Steel')

    # ------------------------------------------------------------------
    # monitoring_data.ods
    # ------------------------------------------------------------------

    def test_monitoring_ods_created(self):
        run_cache_generator(self.well, [GENERATORS.MONITOR])
        self.assertTrue(os.path.exists(monitoring_ods_path(self.well)))

    def test_level_measurements_row_count(self):
        run_cache_generator(self.well, [GENERATORS.MONITOR])
        self.assertEqual(
            get_count(monitoring_ods_path(self.well), 'Groundwater Level'), 2
        )

    def test_quality_measurements_row_count(self):
        run_cache_generator(self.well, [GENERATORS.MONITOR])
        self.assertEqual(
            get_count(monitoring_ods_path(self.well), 'Groundwater Quality'), 1
        )

    def test_yield_measurements_row_count(self):
        run_cache_generator(self.well, [GENERATORS.MONITOR])
        self.assertEqual(
            get_count(monitoring_ods_path(self.well), 'Abstraction-Discharge'),
            1
        )

    def test_level_row_contains_original_id_and_parameter(self):
        run_cache_generator(self.well, [GENERATORS.MONITOR])
        # rows[0] and rows[1] are header rows; rows[2] is the first data row
        all_rows = read_ods_rows(self.well, 'Groundwater Level')
        first_data_row = all_rows[2]
        self.assertEqual(first_data_row[0], 'TEST001')
        self.assertEqual(first_data_row[3], 'Water depth')

    # ------------------------------------------------------------------
    # force_regenerate
    # ------------------------------------------------------------------

    def test_force_regenerate_false_skips_existing(self):
        cache_folder = self.well.data_cache_folder
        os.makedirs(cache_folder, exist_ok=True)
        sentinel_content = {'sentinel': True}
        data_json_path = os.path.join(cache_folder, 'data.json')
        with open(data_json_path, 'w') as data_json_file:
            json.dump(sentinel_content, data_json_file)

        GenerateWellCacheFile(
            self.well, force_regenerate=False,
            generators=[GENERATORS.GENERAL_INFORMATION],
        )

        with open(data_json_path) as data_json_file:
            self.assertEqual(json.load(data_json_file), sentinel_content)

    # ------------------------------------------------------------------
    # partial generators
    # ------------------------------------------------------------------

    def test_monitor_not_created_without_monitor_generator(self):
        run_cache_generator(self.well, [GENERATORS.GENERAL_INFORMATION])
        self.assertFalse(os.path.exists(monitoring_ods_path(self.well)))

    def test_data_json_has_no_general_key_when_only_monitor(self):
        run_cache_generator(self.well, [GENERATORS.MONITOR])
        self.assertNotIn('General Information', load_data_json(self.well))
