import json
import os
import shutil
import time
from shutil import copyfile

from celery import shared_task
from celery.utils.log import get_task_logger
from django.db.models import Value, CharField, Func
from django.utils import timezone
from openpyxl import load_workbook

from gwml2.models.general import Country, Unit
from gwml2.models.term import (
    TermFeatureType, TermWellPurpose, TermWellStatus, TermDrillingMethod,
    TermReferenceElevationType, TermConstructionStructureType,
    TermAquiferType, TermConfinement, TermGroundwaterUse
)
from gwml2.models.well import Well
from gwml2.models.well_management.organisation import Organisation
from gwml2.models.well_quality_control import WellQualityControl
from gwml2.tasks.data_file_cache.base_cache import get_data
from gwml2.tasks.data_file_cache.country_recache import (
    generate_data_country_cache
)
from gwml2.tasks.data_file_cache.organisation_cache import (
    generate_data_organisation_cache
)
from gwml2.tasks.file_lock import file_lock
from gwml2.terms import SheetName
from gwml2.utilities import xlsx_to_ods

DJANGO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
TEMPLATE_FOLDER = os.path.join(DJANGO_ROOT, 'static', 'download_template')

logger = get_task_logger(__name__)


class GENERATORS(object):
    GENERAL_INFORMATION = 'general_information'
    HYDROGEOLOGY = 'hydrogeology'
    MANAGEMENT = 'management'
    DRILLING_AND_CONSTRUCTION = 'drilling_and_construction'
    MONITOR = 'monitor'


class GenerateWellCacheFile(object):
    current_time = None
    monitor_filename = 'monitoring_data.xlsx'

    # cache
    feature_types = {}
    purposes = {}
    status = {}
    units = {}
    drillings = {}
    reference_elevations = {}
    structures_types = {}
    aquifer_types = {}
    confinements = {}
    organisations = {}
    groundwater_uses = {}
    measurement_parameters = {}

    def log(self, text):
        """Print time."""
        new_time = time.time()
        print(f'{text} - {(new_time - self.current_time)} seconds')
        logger.debug(f'{text} - {(new_time - self.current_time)} seconds')
        self.current_time = new_time

    @property
    def folder(self) -> str:
        """Return folder."""
        return self.well.data_cache_folder

    @property
    def country(self) -> Country:
        """Return folder.."""
        return self.well.country

    def _file(self, filename) -> str:
        """Return folder"""
        return os.path.join(self.folder, filename)

    def clean(self):
        """Remove old files"""
        for _file in ['done', 'wells.xlsx', 'drilling_and_construction.xlsx']:
            _folder = os.path.join(self.folder, _file)
            if os.path.exists(_folder):
                if os.path.isfile(_folder):
                    os.remove(_folder)
                elif os.path.isdir(_folder):
                    shutil.rmtree(_folder)

    def copy_template(self, filename):
        """Copy template."""
        copyfile(os.path.join(TEMPLATE_FOLDER, filename), self._file(filename))

    def __init__(
            self, well: Well, force_regenerate: bool = True,
            generators: list = None
    ):
        self.well = well
        self.current_time = time.time()

        lock_id = f'wells_cache_{self.well.id}.lock'
        with file_lock(lock_id) as lock:
            if lock is None:
                return

            _file = os.path.join(self.folder, 'data.json')
            if not force_regenerate and os.path.exists(_file):
                return

            self.log(f'----- Begin cache : id = {self.well.id}  -------')

            # Prepare files
            if not os.path.exists(self.folder):
                os.makedirs(self.folder)

            # Clean files
            self.clean()

            if not generators:
                generators = [
                    GENERATORS.GENERAL_INFORMATION,
                    GENERATORS.HYDROGEOLOGY,
                    GENERATORS.MANAGEMENT,
                    GENERATORS.DRILLING_AND_CONSTRUCTION,
                    GENERATORS.MONITOR
                ]

            self.generators = generators

            # Run the scripts
            self.run()
            self.log(f'----- End cache : id = {self.well.id}  -------')

    def run(self):
        """ Run wells """
        well = self.well
        generated = False

        # General information
        if GENERATORS.GENERAL_INFORMATION in self.generators:
            print(f'Generate {GENERATORS.GENERAL_INFORMATION}')
            self.general_information(well)
            generated = True
        if GENERATORS.HYDROGEOLOGY in self.generators:
            print(f'Generate {GENERATORS.HYDROGEOLOGY}')
            self.hydrogeology(well)
            generated = True
        if GENERATORS.MANAGEMENT in self.generators:
            print(f'Generate {GENERATORS.MANAGEMENT}')
            self.management(well)
            generated = True

        # Drill
        if GENERATORS.DRILLING_AND_CONSTRUCTION in self.generators:
            print(f'Generate {GENERATORS.DRILLING_AND_CONSTRUCTION}')
            self.drilling_and_construction(well)
            generated = True

        # ----------------------------------------
        # Monitor data
        # It is using ods file
        # ----------------------------------------
        if GENERATORS.MONITOR in self.generators:
            print(f'Generate {GENERATORS.MONITOR}')
            self.copy_template(self.monitor_filename)
            monitor_file = self._file(self.monitor_filename)

            # Load workbook for monitoring data
            monitor_book = load_workbook(monitor_file)
            self.measurements(monitor_book, well)
            monitor_book.active = 0
            monitor_book.save(monitor_file)
            monitor_book.close()

            xlsx_to_ods(monitor_file)
            os.remove(monitor_file)
            generated = True

        # Update data cache generated at
        if generated:
            cache = well.cache
            cache.data_cache_generated_at = timezone.now()
            cache.save()

    def write_json(self, sheetname, data):
        """Write JSON by sheetname."""
        _file = os.path.join(self.folder, sheetname + '.json')
        if os.path.exists(_file):
            os.remove(_file)

        _file = os.path.join(self.folder, 'data.json')
        if os.path.exists(_file):
            with open(_file, 'r') as f:
                curr_data = json.load(f)
        else:
            curr_data = {}
        curr_data[sheetname] = data

        # Writing to sample.json
        with open(_file, "w") as outfile:
            outfile.write(json.dumps(curr_data, indent=4))

    def general_information(self, well: Well):
        """General Information of well."""
        sheetname = 'General Information'
        license_obj = well.get_license(convert=True)

        groundwater_level_time_gap = False
        groundwater_level_value_gap = False
        groundwater_level_strange_value = False
        try:
            quality = well.wellqualitycontrol
            groundwater_level_time_gap = quality.groundwater_level_time_gap is not None
            groundwater_level_value_gap = quality.groundwater_level_value_gap is not None
            groundwater_level_strange_value = quality.groundwater_level_strange_value is not None
        except WellQualityControl.DoesNotExist:
            pass
        data = [
            well.original_id,
            well.name,
            get_data(well.organisation_id, self.organisations, Organisation),
            get_data(
                well.feature_type_id, self.feature_types, TermFeatureType
            ),
            get_data(well.purpose_id, self.purposes, TermWellPurpose),
            get_data(well.status_id, self.status, TermWellStatus),
            well.description,
            well.location.y,
            well.location.x,

            # Ground surface elevation
            well.ground_surface_elevation.value if well.ground_surface_elevation else '',
            get_data(
                well.ground_surface_elevation.unit_id, self.units, Unit)
            if well.ground_surface_elevation else '',

            # DEM elevation based on the GLO_90m dataset above sea level
            well.glo_90m_elevation.value if well.glo_90m_elevation else '',
            get_data(
                well.glo_90m_elevation.unit_id, self.units, Unit)
            if well.glo_90m_elevation else '',

            # Top borehole elevation
            well.top_borehole_elevation.value if well.top_borehole_elevation else '',
            get_data(well.top_borehole_elevation.unit_id, self.units, Unit)
            if well.top_borehole_elevation else '',

            # Data quality flag
            'yes' if groundwater_level_time_gap else 'No',
            'yes' if groundwater_level_value_gap else 'No',
            'yes' if groundwater_level_strange_value else 'No',

            # Country
            self.country.code if self.country else '',

            # Address
            well.address,

            # License
            license_obj.license_name,

            # TODO:
            # Change this when measurement type has been added
            # Measurement type

            # Groundwater levels
            well.is_groundwater_level if well.is_groundwater_level else '',
            # Groundwater quality
            well.is_groundwater_quality if well.is_groundwater_quality else '',

            # Measurement data
            well.first_time_measurement.strftime(
                '%Y-%m-%d %H:%M:%S'
            ) if well.first_time_measurement else '',
            well.last_time_measurement.strftime(
                '%Y-%m-%d %H:%M:%S'
            ) if well.last_time_measurement else '',

        ]
        self.write_json(sheetname, [data])

    def hydrogeology(self, well):
        """Hydrogeology of well."""
        hydrogeology = well.hydrogeology_parameter
        pumping_test = hydrogeology.pumping_test if hydrogeology else None
        hydraulic_conductivity = pumping_test.hydraulic_conductivity if pumping_test else None
        transmissivity = pumping_test.transmissivity if pumping_test else None
        specific_storage = pumping_test.specific_storage if pumping_test else None
        specific_capacity = pumping_test.specific_capacity if pumping_test else None
        storativity = pumping_test.storativity if pumping_test else None

        data = [
            well.original_id,
            well.name,
            hydrogeology.aquifer_name if hydrogeology else '',
            hydrogeology.aquifer_material if hydrogeology else '',

            # Aquifer type
            get_data(
                hydrogeology.aquifer_type_id, self.aquifer_types,
                TermAquiferType
            )
            if hydrogeology else '',

            hydrogeology.aquifer_thickness
            if hydrogeology and hydrogeology.aquifer_thickness else '',

            # Aquifer confinement
            get_data(
                hydrogeology.confinement_id, self.confinements,
                TermConfinement
            )
            if hydrogeology else '',

            hydrogeology.degree_of_confinement if hydrogeology else '',

            # Pumping test
            pumping_test.porosity if pumping_test else '',

            hydraulic_conductivity.value if hydraulic_conductivity else '',
            get_data(hydraulic_conductivity.unit_id, self.units, Unit)
            if hydraulic_conductivity else '',

            # transmisivity
            transmissivity.value if transmissivity else '',
            get_data(transmissivity.unit_id, self.units, Unit)
            if transmissivity else '',

            # specific storage
            specific_storage.value if specific_storage else '',
            get_data(specific_storage.unit_id, self.units, Unit)
            if specific_storage else '',

            # specific capacity
            specific_capacity.value if specific_capacity else '',
            get_data(specific_capacity.unit_id, self.units, Unit)
            if specific_capacity else '',

            # specific capacity
            storativity.value if storativity else '',
            get_data(storativity.unit_id, self.units, Unit)
            if storativity else '',

            pumping_test.test_type if pumping_test else '',
        ]

        sheetname = 'Hydrogeology'
        self.write_json(sheetname, [data])

    def management(self, well):
        """Management of well."""
        management = well.management
        data = [
            well.original_id,
            well.name,
            get_data(
                management.groundwater_use_id, self.groundwater_uses,
                TermGroundwaterUse
            ) if management else '',
            management.number_of_users if management else ''
        ]

        sheetname = 'Management'
        self.write_json(sheetname, [data])

    def drilling_and_construction(self, well):
        """Drilling and construction of well."""
        geology = well.geology if well.geology else None
        drilling = well.drilling if well.drilling else None
        construction = well.construction if well.construction else None

        data = [
            well.original_id,
            well.name,

            # Total depth
            geology.total_depth.value if geology and geology.total_depth else '',
            get_data(geology.total_depth.unit_id, self.units, Unit)
            if geology and geology.total_depth else '',

            # Drilling
            get_data(
                drilling.drilling_method_id, self.drillings, TermDrillingMethod
            )
            if drilling and drilling.drilling_method else '',
            drilling.driller if drilling else '',
            (
                'Yes' if drilling.successful else 'No'
            ) if drilling and drilling.successful is not None else '',
            drilling.cause_of_failure if drilling else '',
            drilling.year_of_drilling if drilling else '',
            construction.pump_installer if construction else '',
            construction.pump_description if construction else '',
        ]

        self.write_json(SheetName.drilling_and_construction, [data])

        # --------------------------------------------------------------------------
        # For drilling data
        if drilling:
            # water strike
            sheet_data = []
            sheetname = 'Water Strike'
            for water_strike in well.drilling.waterstrike_set.all():
                depth = water_strike.depth
                data = [
                    well.original_id,
                    well.name,

                    # Depth
                    depth.value if depth else '',
                    get_data(
                        depth.unit_id, self.units, Unit
                    ) if depth else '',
                    get_data(
                        water_strike.reference_elevation_id,
                        self.reference_elevations, TermReferenceElevationType
                    ),
                    (
                        water_strike.description if
                        water_strike.description else ''
                    )
                ]
                sheet_data.append(data)
            self.write_json(sheetname, sheet_data)

            # stratigraphic
            sheet_data = []
            sheetname = 'Stratigraphic Log'
            for log in well.drilling.stratigraphiclog_set.all():
                top_depth = log.top_depth
                bottom_depth = log.bottom_depth
                data = [
                    well.original_id,
                    well.name,

                    # Reference elevation
                    get_data(
                        log.reference_elevation_id, self.reference_elevations,
                        TermReferenceElevationType
                    ),

                    # Top depth
                    top_depth.value if top_depth else '',
                    get_data(top_depth.unit_id, self.units, Unit)
                    if top_depth else '',

                    # Bottom depth
                    bottom_depth.value if bottom_depth else '',
                    get_data(bottom_depth.unit_id, self.units, Unit)
                    if bottom_depth else '',
                    log.material,
                    log.stratigraphic_unit,
                ]
                sheet_data.append(data)
            self.write_json(sheetname, sheet_data)

        # --------------------------------------------------------------------------
        # For Construction Data
        if construction:
            sheetname = SheetName.structure
            sheet_data = []
            for structure in well.construction.constructionstructure_set.all():
                top_depth = structure.top_depth
                bottom_depth = structure.bottom_depth
                diameter = structure.diameter
                data = [
                    well.original_id,
                    well.name,

                    # Structure
                    get_data(
                        structure.type_id, self.structures_types,
                        TermConstructionStructureType
                    ),
                    get_data(
                        structure.reference_elevation_id,
                        self.reference_elevations,
                        TermReferenceElevationType
                    ),

                    # Top depth
                    top_depth.value if top_depth else '',
                    get_data(top_depth.unit_id, self.units, Unit)
                    if top_depth else '',

                    # Bottom depth
                    bottom_depth.value if bottom_depth else '',
                    get_data(bottom_depth.unit_id, self.units, Unit)
                    if bottom_depth else '',

                    # Diameter
                    diameter.value if diameter else '',
                    get_data(diameter.unit_id, self.units, Unit)
                    if diameter else '',
                    structure.material,
                    structure.description
                ]
                sheet_data.append(data)
            self.write_json(sheetname, sheet_data)

    def measurement_data(self, sheets, measurements, original_id, well_name):
        """ Measurements of well """
        measurements = measurements.select_related(
            'parameter', 'value', 'value__unit'
        ).annotate(
            original_id=Value(original_id, output_field=CharField()),
            name=Value(well_name, output_field=CharField()),
            time_str=Func(
                'time',
                Value('YYYY-MM-DD HH24:MI:SS'),
                function='to_char',
                output_field=CharField()
            )
        ).values_list(
            'original_id', 'name',
            'time_str', 'parameter__name',
            'value__value', 'value__unit__name',
            'methodology'
        )
        for measurement in measurements:
            sheets.append(measurement)

    def measurements(self, book, well):
        """ Measurements of well """
        self.measurement_data(
            book['Groundwater Level'],
            well.welllevelmeasurement_set.all(),
            well.original_id,
            well.name
        )
        self.measurement_data(
            book['Groundwater Quality'],
            well.wellqualitymeasurement_set.all(),
            well.original_id,
            well.name
        )
        self.measurement_data(
            book['Abstraction-Discharge'],
            well.wellyieldmeasurement_set.all(),
            well.original_id,
            well.name
        )


@shared_task(bind=True, queue='update')
def generate_data_well_cache(
        self, well_id: int, force_regenerate: bool = True,
        generate_country_cache: bool = True,
        generate_organisation_cache: bool = True,
        generators: list = None
):
    try:
        well = Well.objects.get(id=well_id)
        GenerateWellCacheFile(well, force_regenerate, generators=generators)
        if generate_country_cache and well.country:
            generate_data_country_cache(well.country.code)
        if generate_organisation_cache and well.organisation:
            generate_data_organisation_cache(well.organisation.id)
    except Well.DoesNotExist:
        pass
