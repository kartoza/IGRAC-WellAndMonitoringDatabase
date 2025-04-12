from django.contrib import admin

from gwml2.models.site_preference import SitePreference


@admin.register(SitePreference)
class SitePreferenceAdmin(admin.ModelAdmin):
    """SitePreference Admin."""
    list_display = (
        'parameter_from_ground_surface', 'parameter_from_top_well',
        'parameter_amsl', 'batch_upload_auto_resume'
    )
    list_editable = ('batch_upload_auto_resume',)
