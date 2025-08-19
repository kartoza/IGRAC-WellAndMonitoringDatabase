import json
import os

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from gwml2.models.download_request import WELL_AND_MONITORING_DATA, GGMN
from gwml2.models.general import Country
from gwml2.models.well import Well
from gwml2.tasks.data_file_cache.base_cache import WellCacheZipFileBase

COUNTRY_DATA_FOLDER = os.path.join(settings.GWML2_FOLDER, 'data')


class GenerateCountryCacheFile(WellCacheZipFileBase):
    @property
    def country(self) -> Country:
        """Return country."""
        return self.country_data

    @property
    def cache_type(self) -> str:
        """Return type of cache (country or organisation)."""
        return 'country'

    @property
    def cache_name(self) -> str:
        """Return name of cache object."""
        return self.country.code

    def get_well_queryset(self):
        return Well.objects.filter(
            country=self.country
        ).filter(organisation__isnull=False).order_by('original_id')

    def __init__(self, country):
        self.country_data = country
        self.data_folder = COUNTRY_DATA_FOLDER

    def run(self):
        super(GenerateCountryCacheFile, self).run()
        # generate organisations json file
        organisations = []
        ggmn_organisations = []
        wells = self.get_well_queryset()
        for well in wells:
            if well.is_ggmn():
                ggmn_organisations.append(well.organisation.id)
            else:
                organisations.append(well.organisation.id)

        cache_organisations = {}

        # Save the organisation data
        cache_organisations[
            WELL_AND_MONITORING_DATA] = self.generate_organisations_json_file(
            WELL_AND_MONITORING_DATA, list(set(organisations))
        )
        cache_organisations[GGMN] = self.generate_organisations_json_file(
            GGMN, list(set(ggmn_organisations))
        )
        _file = os.path.join(
            self.data_folder,
            f'{str(self.cache_name)} - organisations.json'
        )
        with open(_file, "w") as outfile:
            outfile.write(json.dumps(cache_organisations, indent=4))

    def generate_organisations_json_file(self, data_type, organisations):
        _file = os.path.join(
            self.data_folder,
            f'{str(self.cache_name)} - {data_type}.json'
        )
        if os.path.exists(_file):
            os.remove(_file)
        return organisations


@shared_task(bind=True, queue='update')
def generate_data_country_cache(self, country_code: str):
    try:
        country = Country.objects.get(code__iexact=country_code)
        generator = GenerateCountryCacheFile(country)
        generator.run()

        # Update data cache generated at
        country.data_cache_generated_at = timezone.now()
        country.save()
    except Country.DoesNotExist:
        print('Country not found')


@shared_task(bind=True, queue='update')
def generate_data_all_country_cache(self):
    for country in Country.objects.all():
        generate_data_country_cache(country.code)
