# Create your tasks here
from gwml2.tasks.clean import clean_download_file
from gwml2.tasks.data_file_cache import (
    generate_data_well_cache, generate_data_country_cache
)
from gwml2.tasks.harvester import run_harvester, run_all_harvester
from gwml2.tasks.uploader.task import well_batch_upload
from gwml2.tasks.well import generate_measurement_cache
