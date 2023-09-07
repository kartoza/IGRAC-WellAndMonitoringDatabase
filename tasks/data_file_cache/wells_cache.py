import json
import os
import shutil
import time
from shutil import copyfile

from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from openpyxl import load_workbook

from geonode.base.models import License, RestrictionCodeType
from gwml2.models.general import Country, Unit
from gwml2.models.term import (
    TermFeatureType, TermWellPurpose, TermWellStatus, TermDrillingMethod,
    TermReferenceElevationType, TermConstructionStructureType,
    TermAquiferType, TermConfinement, TermGroundwaterUse
)
from gwml2.models.term_measurement_parameter import TermMeasurementParameter
from gwml2.models.well import Well
from gwml2.models.well_management.organisation import Organisation
from gwml2.tasks.data_file_cache.base_cache import get_data
from gwml2.tasks.data_file_cache.country_recache import (
    generate_data_country_cache
)

GWML2_FOLDER = settings.GWML2_FOLDER
WELL_FOLDER = os.path.join(GWML2_FOLDER, 'wells-data')
DJANGO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
TEMPLATE_FOLDER = os.path.join(DJANGO_ROOT, 'static', 'download_template')

logger = get_task_logger(__name__)


class GenerateWellCacheFile(object):
    current_time = None
    wells_filename = 'wells.xlsx'
    drill_filename = 'drilling_and_construction.xlsx'
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
        """Return folder.."""
        return os.path.join(WELL_FOLDER, f'{self.well.id}')

    @property
    def country(self) -> Country:
        """Return folder.."""
        return self.well.country

    def _file(self, filename) -> str:
        """Return folder.."""
        return os.path.join(self.folder, filename)

    def copy_template(self, filename):
        """Copy template."""
        copyfile(os.path.join(TEMPLATE_FOLDER, filename), self._file(filename))

    def __init__(self, well: Well, force_regenerate: bool = True):
        self.well = well
        self.current_time = time.time()

        done_file = self._file('done')
        if not force_regenerate and os.path.exists(done_file):
            return
        self.log(f'----- Begin cache : id = {self.well.id}  -------')

        # Prepare files
        if os.path.exists(self.folder):
            shutil.rmtree(self.folder)
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

        # Run the scripts
        self.run()

        # done
        with open(done_file, 'w') as f:
            f.write('Done')

        self.log(f'----- End cache : id = {self.well.id}  -------')

    def run(self):
        """ Run wells """
        well = self.well

        # copy files
        well_folder = self._file(self.wells_filename)

        # General information
        self.general_information(well_folder, well)
        self.hydrogeology(well_folder, well)
        self.management(well_folder, well)

        # Drill
        drill_folder = self._file(self.drill_filename)
        self.drilling_and_construction(drill_folder, well)

        # Monitor
        self.copy_template(self.monitor_filename)
        monitor_file = self._file(self.monitor_filename)
        monitor_book = load_workbook(monitor_file)
        self.measurements(monitor_book, well)
        monitor_book.active = 0
        monitor_book.save(monitor_file)

    def write_json(self, folder, sheetname, data):
        """Write json by sheetname."""
        _file = os.path.join(folder, sheetname + '.json')
        if not os.path.exists(folder):
            os.makedirs(folder)

        if os.path.exists(_file):
            os.remove(_file)

        # Writing to sample.json
        with open(_file, "w") as outfile:
            outfile.write(json.dumps(data, indent=4))

    def general_information(self, folder, well):
        """General Information of well."""
        sheetname = 'General Information'
        license = ''
        if well.license:
            try:
                license = License.objects.get(id=well.license).name
            except License.DoesNotExist:
                pass
        restriction_code_type = ''
        if well.restriction_code_type:
            try:
                restriction_code_type = RestrictionCodeType.objects.get(
                    id=well.restriction_code_type).description
            except RestrictionCodeType.DoesNotExist:
                pass
        data = [
            well.original_id,
            well.name,
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

            # Top borehole elevation
            well.top_borehole_elevation.value if well.top_borehole_elevation else '',
            get_data(well.top_borehole_elevation.unit_id, self.units, Unit)
            if well.top_borehole_elevation else '',
            self.country.code if self.country else '',
            well.address,
            license,
            restriction_code_type,
        ]
        self.write_json(folder, sheetname, [data])

    def hydrogeology(self, folder, well):
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
        self.write_json(folder, sheetname, [data])

    def management(self, folder, well):
        """Management of well."""
        management = well.management
        license = management.license if management else None
        data = [
            well.original_id,
            get_data(well.organisation_id, self.organisations, Organisation),

            # management
            management.manager if management else '',
            management.description if management else '',
            get_data(
                management.groundwater_use_id, self.groundwater_uses,
                TermGroundwaterUse
            ) if management else '',
            management.number_of_users if management else '',

            license.number if license else '',
            license.valid_from.strftime('%Y-%m-%d')
            if license and license.valid_from else '',
            license.valid_until.strftime('%Y-%m-%d')
            if management and license and license.valid_until else '',
            license.description if license else '',
        ]

        sheetname = 'Management'
        self.write_json(folder, sheetname, [data])

    def drilling_and_construction(self, folder, well):
        """Drilling and construction of well."""
        geology = well.geology if well.geology else None
        drilling = well.drilling if well.drilling else None
        construction = well.construction if well.construction else None

        data = [
            well.original_id,

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
        sheetname = 'Drilling and Construction'
        self.write_json(folder, sheetname, [data])

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

                    # Depth
                    depth.value if depth else '',
                    get_data(
                        depth.unit_id, self.units, Unit
                    ) if depth else '',
                    get_data(
                        water_strike.reference_elevation_id,
                        self.reference_elevations, TermReferenceElevationType
                    ),
                ]
                sheet_data.append(data)
            self.write_json(folder, sheetname, sheet_data)

            # stratigraphic
            sheet_data = []
            sheetname = 'Stratigraphic Log'
            for log in well.drilling.stratigraphiclog_set.all():
                top_depth = log.top_depth
                bottom_depth = log.bottom_depth
                data = [
                    well.original_id,

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
            self.write_json(folder, sheetname, sheet_data)

        # --------------------------------------------------------------------------
        # For Construction Data
        if construction:
            sheetname = 'Structures'
            sheet_data = []
            for structure in well.construction.constructionstructure_set.all():
                top_depth = structure.top_depth
                bottom_depth = structure.bottom_depth
                diameter = structure.diameter
                data = [
                    well.original_id,

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
            self.write_json(folder, sheetname, sheet_data)

    def measurement_data(self, sheets, measurements, original_id):
        """ Measurements of well """
        for measurement in measurements:
            value = measurement.value
            data = [
                original_id,

                # measurement
                measurement.time.strftime('%Y-%m-%d %H:%M:%S %Z'),
                get_data(
                    measurement.parameter_id, self.measurement_parameters,
                    TermMeasurementParameter
                ),

                # value
                value.value if value else '',
                get_data(value.unit_id, self.units, Unit) if value else '',
                measurement.methodology
            ]
            sheets.append(data)

    def measurements(self, book, well):
        """ Measurements of well """
        self.measurement_data(
            book['Groundwater Level'],
            well.welllevelmeasurement_set.all(),
            well.original_id
        )
        self.measurement_data(
            book['Groundwater Quality'],
            well.wellqualitymeasurement_set.all(),
            well.original_id
        )
        self.measurement_data(
            book['Abstraction-Discharge'],
            well.wellyieldmeasurement_set.all(),
            well.original_id
        )


@shared_task(bind=True, queue='update')
def generate_data_well_cache(
        self, well_id: int, force_regenerate: bool = True,
        generate_country_cache: bool = True
):
    try:
        well = Well.objects.get(id=well_id)
        GenerateWellCacheFile(well, force_regenerate)
        if generate_country_cache and well.country:
            generate_data_country_cache(well.country.code)
    except Well.DoesNotExist:
        pass
