from django.contrib import admin
from django.contrib.auth import get_user_model

from gwml2.forms.organisation import OrganisationFormAdmin
from gwml2.models.well_management.organisation import (
    Organisation, OrganisationType, OrganisationLink, OrganisationGroup
)
from gwml2.utils.management_commands import run_command

User = get_user_model()


def reassign_wells_country(modeladmin, request, queryset):
    """Reassign wells country by the organisation country."""
    for org in queryset.filter(country__isnull=False):
        org.well_set.all().update(country=org.country)


def generate_data_wells_cache(modeladmin, request, queryset):
    """Generate measurement cache."""
    ids = [f'{_id}' for _id in queryset.values_list('id', flat=True)]
    return run_command(
        request,
        'generate_data_organisations_cache',
        args=[
            "--ids", ', '.join(ids), "--force"
        ]
    )


@admin.action(description='Update ggis uid of wells')
def update_ggis_uid(modeladmin, request, queryset):
    """Update ggis uid."""
    from gwml2.tasks.organisation import update_ggis_uid
    for org in queryset:
        update_ggis_uid.delay(org.id)


def assign_data(modeladmin, request, queryset):
    """Assign data to the organisation."""
    for org in queryset:
        org.assign_data()


class OrganisationLinkInline(admin.TabularInline):
    """OrganisationLinkInline."""
    model = OrganisationLink


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    """Admin for Organisation model."""
    list_display = (
        'name', 'description', 'links', 'data_types', 'time_range',
        'license_name', 'active', 'country', 'well_number',
        'data_cache_generated_at'
    )
    list_editable = ('active',)
    list_filter = ('data_cache_generated_at', 'country')
    search_fields = ('name',)
    actions = (
        generate_data_wells_cache, reassign_wells_country, update_ggis_uid,
        assign_data
    )
    inlines = [OrganisationLinkInline]
    form = OrganisationFormAdmin

    def well_number(self, org: Organisation):
        return org.well_set.all().count()

    def links(self, org: Organisation):
        return list(
            org.links.values_list('url', flat=True)
        )


@admin.register(OrganisationGroup)
class OrganisationGroupAdmin(admin.ModelAdmin):
    """Admin for OrganisationGroup model."""
    list_display = (
        'name', '_organisations'
    )
    filter_horizontal = ('organisations',)

    def _organisations(self, org: OrganisationGroup):
        """Return organisations in the group."""
        return list(org.organisations.all().values_list('name', flat=True))


admin.site.register(OrganisationType, admin.ModelAdmin)
