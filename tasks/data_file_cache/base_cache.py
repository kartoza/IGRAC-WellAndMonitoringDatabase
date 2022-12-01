import os
import time
from shutil import copyfile

from celery.utils.log import get_task_logger

from gwml2.models.download_request import WELL_AND_MONITORING_DATA, GGMN
from gwml2.models.term import TermFeatureType

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
        """Return folder.."""
        raise NotImplemented

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
        copyfile(os.path.join(TEMPLATE_FOLDER, filename), well_file)
        copyfile(os.path.join(TEMPLATE_FOLDER, filename), ggmn_file)

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
