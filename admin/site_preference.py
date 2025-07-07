from django.contrib import admin

from gwml2.models.site_preference import SitePreference
from gwml2.tasks.harvester import run_all_harvester


@admin.action(description='Update running harvesters')
def update_running_harvester(modeladmin, request, queryset):
    SitePreference.update_running_harvesters()


@admin.action(description='Running all harvesters')
def running_all_harvesters(modeladmin, request, queryset):
    run_all_harvester()


@admin.register(SitePreference)
class SitePreferenceAdmin(admin.ModelAdmin):
    """SitePreference Admin."""
    list_display = (
        'parameter_from_ground_surface', 'parameter_from_top_well',
        'parameter_amsl', 'batch_upload_auto_resume', '_running_harvesters'
    )
    list_editable = ('batch_upload_auto_resume',)
    filter_horizontal = ('running_harvesters',)
    actions = (update_running_harvester, running_all_harvesters)

    def _running_harvesters(self, obj: SitePreference):
        """Running harvesters."""
        if not obj.running_harvesters.count():
            return None
        return [harvester.name for harvester in obj.running_harvesters.all()]
