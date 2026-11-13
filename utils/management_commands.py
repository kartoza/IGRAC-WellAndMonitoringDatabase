from django.http import HttpResponseRedirect

from geonode.management_commands_http.models import ManagementCommandJob
from geonode.management_commands_http.utils.jobs import start_task


def run_command_background(command: str, args: list, user_id: int = None):
    """Create a ManagementCommandJob and start it after the current transaction commits."""
    from django.contrib.auth import get_user_model
    from django.db import transaction
    from gwml2.apps import GroundwaterConfig

    if user_id is None:
        user_id = get_user_model().objects.filter(
            is_superuser=True
        ).order_by('id').values_list('id', flat=True).first()

    if not user_id:
        return

    def _start():
        obj = ManagementCommandJob.objects.create(
            command=command,
            app_name=GroundwaterConfig.name,
            args=args,
            user_id=user_id
        )
        start_task(obj)

    transaction.on_commit(_start)


def refresh_mv_well_background(user_id: int = None):
    """Refresh mv_well materialized view in background."""
    run_command_background(
        'refresh_materialized_views', ['mv_well'], user_id=user_id
    )


def run_command(request, command: str, args: list):
    """Run the management command."""
    from gwml2.apps import GroundwaterConfig
    obj = ManagementCommandJob.objects.create(
        command=command,
        app_name=GroundwaterConfig.name,
        args=args,
        user_id=request.user.id
    )
    start_task(obj)
    return HttpResponseRedirect(
        f'/en-us/admin/management_commands_http/'
        f'managementcommandjob/{obj.id}/change/'
    )
