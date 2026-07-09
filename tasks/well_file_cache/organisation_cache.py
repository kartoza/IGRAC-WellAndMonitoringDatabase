import os

from celery import shared_task
from django.conf import settings

from gwml2.models.well import Well
from gwml2.models.well_management.organisation import Organisation
from gwml2.tasks.well_file_cache.well_zipped_cache import WellZippedCache

ORGANISATION_DATA_FOLDER = os.path.join(
    settings.GWML2_FOLDER, 'organisation-data'
)


class GenerateOrganisationCacheFile(WellZippedCache):
    organisation = None
    data_folder = ORGANISATION_DATA_FOLDER

    @property
    def cache_name(self) -> str:
        """Return name of cache object."""
        return self.organisation.name

    @property
    def well_queryset(self):
        return Well.objects.select_related(
            'organisation'
        ).filter(organisation=self.organisation).order_by('-id')

    def __init__(self, organisation):
        self.organisation = organisation


@shared_task(bind=True, queue='update')
def generate_data_organisation_cache(self, organisation_id: int):
    try:
        organisation = Organisation.objects.get(id=organisation_id)
        generator = GenerateOrganisationCacheFile(organisation)
        generator.run()
        organisation.assign_metadata_cache()
    except Organisation.DoesNotExist:
        print('Country not found')


@shared_task(bind=True, queue='update')
def generate_data_all_organisation_cache(self):
    for organisation in Organisation.objects.all():
        generate_data_organisation_cache(organisation.id)
