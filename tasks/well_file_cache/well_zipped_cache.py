import json
import os
import shutil
import time
import zipfile

from celery.utils.log import get_task_logger

from gwml2.terms import SheetName
from gwml2.utils.ods_writer import OdsDoc

DJANGO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
TEMPLATE_FOLDER = os.path.join(DJANGO_ROOT, 'static', 'download_template')

logger = get_task_logger(__name__)


class WellZippedCache(object):
    current_time = None
    wells_filename = 'wells.ods'
    drill_filename = 'drilling_and_construction.ods'
    monitor_filename = 'monitoring_data.ods'

    @property
    def data_folder(self) -> str:
        """Return data folder path."""
        raise NotImplementedError

    def filepath(self, filename):
        """Get file on folder."""
        return os.path.join(self.folder, filename)

    def clean(self):
        """Remove all temporary files and folders."""
        if os.path.exists(self.folder):
            try:
                shutil.rmtree(self.folder)
            except FileNotFoundError:
                pass

    def copy_template(self, filename):
        """Copy template."""
        shutil.copyfile(
            os.path.join(TEMPLATE_FOLDER, filename), self.filepath(filename)
        )

    def log(self, text):
        """Print time."""
        new_time = time.time()
        print(f'{text} - {(new_time - self.current_time)} seconds')
        logger.debug(f'{text} - {(new_time - self.current_time)} seconds')
        self.current_time = new_time

    @property
    def cache_name(self) -> str:
        """Return name of cache object."""
        raise NotImplementedError

    @property
    def well_queryset(self):
        """Return queryset for wells."""
        raise NotImplementedError

    @property
    def folder(self) -> str:
        """Return folder."""
        return os.path.join(self.data_folder, self.cache_name)

    @property
    def zip_file_path(self) -> str:
        """Return path to the final zip file."""
        return os.path.join(self.data_folder, f'{self.cache_name}.zip')

    def merge_data_per_well(self, well, filename, well_book, sheets):
        """Merge data per well."""
        well_folder = well.data_cache_folder

        well_data = None
        data_file = os.path.join(well_folder, 'data.json')
        if os.path.exists(data_file):
            try:
                with open(data_file, 'r') as f:
                    well_data = json.load(f)
            except (json.JSONDecodeError, OSError):
                pass

        for sheetname in sheets:
            self.merge_data_between_sheets(
                well_data,
                os.path.join(well_folder, filename), well_book, sheetname
            )

    def merge_data_between_sheets(
            self, well_data, source_folder, target_book, sheetname
    ):
        """Merge data between sheets."""
        target_column_number = SheetName().get_column_size(
            sheet_name=sheetname
        )

        if well_data:
            try:
                data = well_data[sheetname]
            except KeyError:
                return
        else:
            if not os.path.exists(source_folder) or not target_book:
                return
            source_file = os.path.join(source_folder, f'{sheetname}.json')
            if not os.path.exists(source_file):
                return
            with open(source_file, 'r') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    return

        if not target_book:
            return

        target_sheet = target_book[sheetname]
        for row in data:
            if len(row) != target_column_number:
                continue
            target_sheet.append(row)

    def zip_ods(self, zip_file, filename):
        """Add ods file directly to zip."""
        zip_file.write(
            self.filepath(filename), filename, compress_type=zipfile.ZIP_STORED
        )

    def run(self, post_function=None):
        self.current_time = time.time()
        self.log(f'----- {self.cache_name} : Begin cache -------')

        # clear everything before starts
        self.clean()

        # Prepare folder
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

        # Copy ods templates
        self.copy_template(self.wells_filename)
        self.copy_template(self.drill_filename)

        # Open ods docs
        well_book = OdsDoc(self.filepath(self.wells_filename))
        drilling_book = OdsDoc(self.filepath(self.drill_filename))

        # Merge data from each well's data.json into ods docs
        total = self.well_queryset.count()
        for idx, well in enumerate(self.well_queryset, start=1):
            print(
                f'{self.cache_name} : Processing : '
                f'{idx}/{total} {well.original_id} - well book'
            )
            self.merge_data_per_well(
                well, self.wells_filename, well_book,
                [
                    SheetName.general_information,
                    SheetName.hydrogeology,
                    SheetName.management
                ]
            )
            print(
                f'{self.cache_name} : Processing : '
                f'{idx}/{total} {well.original_id} - drilling book'
            )
            self.merge_data_per_well(
                well, self.drill_filename, drilling_book,
                [
                    SheetName.drilling_and_construction,
                    SheetName.water_strike,
                    SheetName.stratigraphic_log,
                    SheetName.structure
                ]
            )

        # Save ods files
        well_book.save()
        well_book.close()
        drilling_book.save()
        drilling_book.close()

        self.log(f'-- {self.cache_name} : Finish merging well ----')

        # Zip files
        zip_filepath = self.zip_file_path
        if os.path.exists(zip_filepath):
            os.remove(zip_filepath)

        zip_file = None
        try:
            original_ids_found = {}
            for well in self.well_queryset:
                if not zip_file:
                    zip_file = zipfile.ZipFile(zip_filepath, 'w')
                    self.zip_ods(zip_file, self.wells_filename)
                    self.zip_ods(zip_file, self.drill_filename)

                if well.number_of_measurements == 0:
                    continue

                measurement_file = os.path.join(
                    well.data_cache_folder, self.monitor_filename
                )
                if os.path.exists(measurement_file):
                    original_id = well.original_id
                    try:
                        _filename = (
                            f'monitoring/{original_id} '
                            f'({original_ids_found[original_id] + 1}).ods'
                        )
                    except KeyError:
                        _filename = f'monitoring/{original_id}.ods'
                        original_ids_found[original_id] = 0

                    zip_file.write(
                        measurement_file,
                        _filename,
                        compress_type=zipfile.ZIP_STORED
                    )
            if post_function:
                post_function(zip_file)
        except Exception as e:
            raise e
        finally:
            if zip_file:
                zip_file.close()

        self.log(f'---- {self.cache_name} :Finish zipping ------')

        # clear temp directory
        self.clean()


class WellZippedCacheByIds(WellZippedCache):
    """Cache wells by ids."""

    data_folder = None
    cache_name = None
    well_queryset = None

    def __init__(self, data_folder, cache_name, well_queryset):
        self.data_folder = data_folder
        self.cache_name = cache_name
        self.well_queryset = well_queryset
