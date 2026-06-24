import json
import os

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from gwml2.models.general import Country
from gwml2.models.well import Well
from gwml2.tasks.well_file_cache.well_zipped_cache import WellZippedCache

COUNTRY_DATA_FOLDER = os.path.join(settings.GWML2_FOLDER, 'country-data')


class GenerateCountryCacheFile(WellZippedCache):
    """Generate country cache file."""
    data_folder = COUNTRY_DATA_FOLDER
    country = None

    @property
    def cache_name(self) -> str:
        """Return name of cache object."""
        return self.country.code

    @property
    def well_queryset(self):
        return Well.objects.filter(
            country=self.country
        ).filter(organisation__isnull=False).order_by('original_id')

    def __init__(self, country):
        self.country = country

    def run(self):
        super(GenerateCountryCacheFile, self).run()
        # generate organisations json file
        organisations = list(
            self.well_queryset.values_list('organisation_id', flat=True)
        )
        _file = os.path.join(
            self.data_folder,
            f'{str(self.cache_name)} - metadata.json'
        )
        with open(_file, "w") as outfile:
            outfile.write(
                json.dumps(
                    {'organisations': list(set(organisations))},
                    indent=4)
            )


@shared_task(bind=True, queue='update')
def generate_data_country_cache(self, country_code: str):
    try:
        country = Country.objects.get(code__iexact=country_code)
        generator = GenerateCountryCacheFile(country)
        generator.run()
        country.assign_data()
    except Country.DoesNotExist:
        print('Country not found')


@shared_task(bind=True, queue='update')
def generate_data_all_country_cache(self):
    for country in Country.objects.all():
        generate_data_country_cache(country.code)
