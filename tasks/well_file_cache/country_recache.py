import json
import os

from celery import shared_task
from django.conf import settings

from gwml2.models.general import Country
from gwml2.models.well import Well
from gwml2.models.well_management.organisation import OrganisationGroup
from gwml2.tasks.well_file_cache.well_zipped_cache import WellZippedCache

COUNTRY_DATA_FOLDER = os.path.join(settings.GWML2_FOLDER, 'country-data')


class GenerateCountryCacheFile(WellZippedCache):
    """Generate country cache file."""
    data_folder = COUNTRY_DATA_FOLDER
    country = None
    is_ggmn = None

    @property
    def cache_name(self) -> str:
        """Return name of cache object."""
        if self.is_ggmn:
            return f'{self.country.code}-ggmn'
        return self.country.code

    @property
    def well_queryset(self):
        queryset = Well.objects.filter(
            country=self.country
        ).filter(organisation__isnull=False)
        group = OrganisationGroup.get_ggmn_group()
        if group:
            if self.is_ggmn:
                queryset = queryset.filter(
                    organisation__in=group.organisations.all()
                )
            else:
                queryset = queryset.exclude(
                    organisation__in=group.organisations.all()
                )
        return queryset.order_by('original_id')

    def __init__(self, country, is_ggmn):
        self.country = country
        self.is_ggmn = is_ggmn

    def run(self):
        super(GenerateCountryCacheFile, self).run()
        # generate organisations json file
        organisations = list(
            self.well_queryset.values_list('organisation_id', flat=True)
        )
        _file = os.path.join(
            self.data_folder,
            f'{self.country.code} - metadata.json'
        )
        metadata = {}
        if os.path.exists(_file):
            try:
                with open(_file, 'r') as f:
                    metadata = json.load(f)
            except (json.JSONDecodeError, OSError):
                metadata = {}

        if self.is_ggmn:
            metadata['organisations-ggmn'] = list(set(organisations))
        else:
            metadata['organisations'] = list(set(organisations))

        with open(_file, 'w') as outfile:
            outfile.write(json.dumps(metadata, indent=4))


@shared_task(bind=True, queue='update')
def generate_data_country_cache(self, country_code: str):
    try:
        country = Country.objects.get(code__iexact=country_code)
        # For non GGMN
        generator = GenerateCountryCacheFile(country, False)
        generator.run()

        # For GGMN
        generator = GenerateCountryCacheFile(country, True)
        generator.run()

        country.assign_data()
    except Country.DoesNotExist:
        print('Country not found')


@shared_task(bind=True, queue='update')
def generate_data_all_country_cache(self):
    for country in Country.objects.all():
        generate_data_country_cache(country.code)
