import json
import os

from celery import shared_task
from django.conf import settings

from gwml2.models.download_request import WELL_AND_MONITORING_DATA, GGMN
from gwml2.models.general import Country
from gwml2.models.well import Well
from gwml2.tasks.data_file_cache.base_cache import WellCacheZipFileBase

COUNTRY_DATA_FOLDER = os.path.join(settings.GWML2_FOLDER, 'country-data')


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
        return Well.objects.select_related(
            'organisation').filter(country=self.country).order_by('-id')

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
            if (
                well.organisation and
                well.organisation.name not in organisations
            ):
                organisations.append(well.organisation.name)
            if (
                well.organisation and well.number_of_measurements > 0 and
                well.organisation.name not in ggmn_organisations
            ):
                ggmn_organisations.append(well.organisation.name)
        self.generate_organisations_json_file(WELL_AND_MONITORING_DATA,
                                              organisations)
        self.generate_organisations_json_file(GGMN, ggmn_organisations)

    def generate_organisations_json_file(self, data_type, organisations):
        _file = os.path.join(self.data_folder,
                             f'{str(self.cache_name)} - {data_type}.json')
        with open(_file, "w") as outfile:
            outfile.write(json.dumps(organisations, indent=4))


@shared_task(bind=True, queue='update')
def generate_data_country_cache(self, country_code: str):
    try:
        country = Country.objects.get(code__iexact=country_code)
        generator = GenerateCountryCacheFile(country)
        generator.run()
    except Country.DoesNotExist:
        print('Country not found')
