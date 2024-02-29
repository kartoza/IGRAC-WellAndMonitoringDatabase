import os
import time
import json
import shutil
import zipfile

from celery.utils.log import get_task_logger
from openpyxl import load_workbook

from django.conf import settings
from gwml2.models.download_request import WELL_AND_MONITORING_DATA, GGMN
from gwml2.models.term import TermFeatureType


GWML2_FOLDER = settings.GWML2_FOLDER
WELL_FOLDER = os.path.join(GWML2_FOLDER, 'wells-data')
DJANGO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
TEMPLATE_FOLDER = os.path.join(DJANGO_ROOT, 'static', 'download_template')

logger = get_task_logger(__name__)


def zipdir(path, ziph):
    """Zip directory"""
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(
                os.path.join(root, file),
                os.path.relpath(
                    os.path.join(root, file), os.path.join(path, '..')
                )
            )


def get_data(id, cache, Term):
    """Get data that on cache or not."""
    if not id:
        return ''
    if id not in cache:
        try:
            value = Term.objects.get(id=id).__str__()
        except TermFeatureType.DoesNotExist:
            value = ''
        cache[id] = value
        return value
    return cache[id]


class WellCacheFileBase(object):
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

    @property
    def folder(self) -> str:
        """Return temporary working directory."""
        raise NotImplementedError

    def folder_by_type(self, data_type):
        """Return folder by type."""
        return os.path.join(self.folder, data_type)

    def file_by_type(self, filename, data_type):
        """Get file of on folder."""
        return os.path.join(self.folder_by_type(data_type), filename)

    def copy_template(self, filename):
        """Copy template."""
        well_file = self.file_by_type(filename, WELL_AND_MONITORING_DATA)
        ggmn_file = self.file_by_type(filename, GGMN)

        # Delete existed file
        if os.path.exists(well_file):
            os.remove(well_file)
        if os.path.exists(ggmn_file):
            os.remove(ggmn_file)

        # Copy the template
        shutil.copyfile(os.path.join(TEMPLATE_FOLDER, filename), well_file)
        shutil.copyfile(os.path.join(TEMPLATE_FOLDER, filename), ggmn_file)

    def return_well_and_ggmn_files(self, well, filename):
        """Return well and ggmn files"""
        well_file = self.file_by_type(filename, WELL_AND_MONITORING_DATA)
        ggmn_file = None
        if well.number_of_measurements > 0 and well.organisation:
            ggmn_file = self.file_by_type(filename, GGMN)
        return well_file, ggmn_file

    def log(self, text):
        """Print time."""
        new_time = time.time()
        print(f'{text} - {(new_time - self.current_time)} seconds')
        logger.debug(f'{text} - {(new_time - self.current_time)} seconds')
        self.current_time = new_time


class WellCacheZipFileBase(WellCacheFileBase):
    data_folder = None

    @property
    def cache_type(self) -> str:
        """Return type of cache (country or organisation)."""
        raise NotImplementedError

    @property
    def cache_name(self) -> str:
        """Return name of cache object."""
        raise NotImplementedError

    @property
    def folder(self) -> str:
        """Return folder.."""
        return os.path.join(self.data_folder, self.cache_name)

    def zip_file_path(self, data_type) -> str:
        """Return path to the final zip file."""
        zip_filename = f'{self.cache_name} - {data_type}.zip'
        return os.path.join(self.data_folder, zip_filename)

    def get_well_queryset(self):
        """Return queryset for wells."""
        raise NotImplementedError

    def merge_data_per_well(
            self, well, filename, well_book, ggmn_book, sheets
    ):
        """Merge data per well.."""
        well_folder = os.path.join(WELL_FOLDER, f'{well.id}')
        for sheetname in sheets:
            self.merge_data_between_sheets(
                os.path.join(well_folder, filename),
                well_book, ggmn_book, sheetname
            )
        well_book.active = 0
        if ggmn_book:
            ggmn_book.active = 0

    def merge_data_between_sheets(
            self, source_file, target_book, target_book_2, sheetname
    ):
        """Merge data between sheets"""
        if not os.path.exists(source_file) or not target_book:
            return
        source_file = os.path.join(source_file, sheetname + '.json')
        data = []
        if os.path.exists(source_file):
            _file = open(source_file, "r")
            data = json.loads(_file.read())

        # Target book 1
        target_sheet = target_book[sheetname]

        # Target book 2
        target_sheet_2 = None
        if target_book_2:
            target_sheet_2 = target_book_2[sheetname]

        # Append data from source
        for row in data:
            target_sheet.append(row)
            if target_book_2:
                target_sheet_2.append(row)

    def clear_folder(self):
        if os.path.exists(self.folder):
            try:
                shutil.rmtree(self.folder)
            except FileNotFoundError:
                pass

    def run(self):
        self.current_time = time.time()
        self.log(
            f'----- Begin cache {self.cache_type}: {self.cache_name} '
            '-------'
        )
        # clear everything before starts
        self.clear_folder()

        # Prepare files
        well_folder = self.folder_by_type(WELL_AND_MONITORING_DATA)
        if not os.path.exists(well_folder):
            os.makedirs(well_folder)

        ggmn_folder = self.folder_by_type(GGMN)
        if not os.path.exists(ggmn_folder):
            os.makedirs(ggmn_folder)

        # copy files
        self.copy_template(self.wells_filename)
        self.copy_template(self.drill_filename)

        # Get data
        # Well files
        well_file = self.file_by_type(
            self.wells_filename, WELL_AND_MONITORING_DATA)
        well_book = load_workbook(well_file)
        well_ggmn_file = self.file_by_type(self.wells_filename, GGMN)
        well_ggmn_book = load_workbook(well_ggmn_file)

        # Drilling files
        drilling_file = self.file_by_type(
            self.drill_filename, WELL_AND_MONITORING_DATA)
        drilling_book = load_workbook(drilling_file)
        drilling_ggmn_file = self.file_by_type(self.drill_filename, GGMN)
        drilling_ggmn_book = load_workbook(drilling_ggmn_file)

        # Save the data
        wells = self.get_well_queryset()
        for well in wells:
            self.merge_data_per_well(
                well, self.wells_filename, well_book,
                well_ggmn_book if well.number_of_measurements > 0 and
                well.organisation else None,
                ['General Information', 'Hydrogeology', 'Management']
            )
            self.merge_data_per_well(
                well, self.drill_filename, drilling_book,
                drilling_ggmn_book if well.number_of_measurements > 0 and
                well.organisation else None,
                ['Drilling and Construction', 'Water Strike',
                 'Stratigraphic Log', 'Structures']
            )

        # Save book
        well_book.save(well_file)
        well_ggmn_book.save(well_ggmn_file)
        drilling_book.save(drilling_file)
        drilling_ggmn_book.save(drilling_ggmn_file)

        # -------------------------------------------------------------------------
        # zipping files
        # -------------------------------------------------------------------------
        self.log(
            f'----- Finish constructing {self.cache_type}: {self.cache_name} '
            '------'
        )
        for data_type in [WELL_AND_MONITORING_DATA, GGMN]:
            zip_file = self.zip_file_path(data_type)
            if os.path.exists(zip_file):
                os.remove(zip_file)
            zip_file = zipfile.ZipFile(zip_file, 'w')

            well_file = self.file_by_type(self.wells_filename, data_type)
            zip_file.write(
                well_file, self.wells_filename,
                compress_type=zipfile.ZIP_DEFLATED)

            drill_file = self.file_by_type(self.drill_filename, data_type)
            zip_file.write(
                drill_file,
                self.drill_filename,
                compress_type=zipfile.ZIP_DEFLATED)

            original_ids_found = {}
            wells = self.get_well_queryset()
            for well in wells:
                if well.number_of_measurements == 0:
                    continue
                well_folder = os.path.join(WELL_FOLDER, f'{well.id}')
                measurement_file = os.path.join(
                    well_folder, self.monitor_filename
                )
                if os.path.exists(measurement_file):
                    original_id = well.original_id
                    try:
                        _filename = (
                            f'monitoring/{original_id} '
                            f'({original_ids_found[original_id] + 1}).xlsx'
                        )
                        continue
                    except KeyError:
                        _filename = f'monitoring/{original_id}.xlsx'
                        original_ids_found[original_id] = 0

                    zip_file.write(
                        measurement_file,
                        _filename,
                        compress_type=zipfile.ZIP_DEFLATED
                    )
            zip_file.close()
        self.log(
            f'----- Finish zipping {self.cache_type}: {self.cache_name} '
            '-------'
        )

        # clear temp directory
        self.clear_folder()
