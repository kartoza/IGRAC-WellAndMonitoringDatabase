""" Quality well control.
"""

from django.core.exceptions import PermissionDenied
from django.views.generic.list import View

from gwml2.utils.management_commands import run_command


class GenerateQualityControlMissingOneView(View):
    """Generate missing one on in view."""

    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied()

        return run_command(
            request,
            'generate_well_quality_control',
            args=[]
        )
