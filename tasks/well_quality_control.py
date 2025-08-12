from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model

from geonode.management_commands_http.models import ManagementCommandJob
from geonode.management_commands_http.utils.jobs import start_task
from gwml2.tasks.file_lock import file_lock

logger = get_task_logger(__name__)
User = get_user_model()

LOCK_ID = 'run_well_quality_control.lock'


@shared_task(
    bind=True,
    name='gwml2.tasks.well.run_well_quality_control',
    queue='update',
    acks_late=False,
    autoretry_for=(),
    max_retries=0
)
def run_well_quality_control(self):
    """Run well quality control."""
    with file_lock(LOCK_ID) as lock:
        if lock is None:
            return
        from gwml2.apps import GroundwaterConfig
        obj = ManagementCommandJob.objects.create(
            command="generate_well_quality_control",
            app_name=GroundwaterConfig.name,
            args=[
                "--ids", '9272',
                '--force'
            ],
            user_id=User.objects.get(username='admin').id
        )
        start_task(obj)
