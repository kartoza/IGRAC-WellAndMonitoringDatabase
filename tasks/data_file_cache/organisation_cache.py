import os

from celery import shared_task
from django.conf import settings

from gwml2.models.well import Well
from gwml2.models.well_management.organisation import Organisation
from gwml2.tasks.data_file_cache.base_cache import WellCacheZipFileBase
from django.utils import timezone

ORGANISATION_DATA_FOLDER = os.path.join(
    settings.GWML2_FOLDER, 'organisation-data'
)


class GenerateOrganisationCacheFile(WellCacheZipFileBase):
    @property
    def organisation(self) -> Organisation:
        """Return organisation."""
        return self.organisation_data

    @property
    def cache_type(self) -> str:
        """Return type of cache (country or organisation)."""
        return 'organisation'

    @property
    def cache_name(self) -> str:
        """Return name of cache object."""
        return self.organisation.name

    def get_well_queryset(self):
        return Well.objects.select_related(
            'organisation'
        ).filter(organisation=self.organisation).order_by('-id')

    def __init__(self, organisation):
        self.organisation_data = organisation
        self.data_folder = ORGANISATION_DATA_FOLDER


@shared_task(bind=True, queue='update')
def generate_data_organisation_cache(self, organisation_id: int):
    try:
        organisation = Organisation.objects.get(id=organisation_id)
        generator = GenerateOrganisationCacheFile(organisation)
        generator.run()

        # Update data cache generated at
        organisation.data_cache_generated_at = timezone.now()
        organisation.save()
    except Organisation.DoesNotExist:
        print('Country not found')


@shared_task(bind=True, queue='update')
def generate_data_all_organisation_cache(self):
    for organisation in Organisation.objects.all():
        generate_data_organisation_cache(organisation.id)
