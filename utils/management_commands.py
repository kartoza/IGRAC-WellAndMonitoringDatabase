from django.http import HttpResponseRedirect

from geonode.management_commands_http.models import ManagementCommandJob
from geonode.management_commands_http.utils.jobs import start_task


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
