import json

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html

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


def assign_data_types(modeladmin, request, queryset):
    """Assign data to the organisation."""
    for org in queryset:
        org.assign_data_types()


def assign_date_range(modeladmin, request, queryset):
    """Assign data to the organisation."""
    for org in queryset:
        org.assign_date_range()


def assign_license(modeladmin, request, queryset):
    """Assign data to the organisation."""
    for org in queryset:
        org.assign_license()


class OrganisationLinkInline(admin.TabularInline):
    """OrganisationLinkInline."""
    model = OrganisationLink


def generate_organisation_cache_information(modeladmin, request, queryset):
    """Generate measurement cache."""
    ids = [f'{_id}' for _id in queryset.values_list('id', flat=True)]
    return run_command(
        request,
        'generate_organisation_cache_information',
        args=[
            "--ids", ', '.join(ids), "--force"
        ]
    )


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    """Admin for Organisation model."""
    list_display = (
        'name', 'data_types', 'time_range',
        'license_name', 'active', 'country', '_groups', 'description',
        'data_cache_generated_at', 'links', 'data_cache_info'
    )
    list_editable = ('active',)
    list_filter = ('data_cache_generated_at', 'country')
    search_fields = ('name',)
    actions = (
        generate_data_wells_cache, reassign_wells_country, update_ggis_uid,
        assign_data_types, assign_date_range, assign_license,
        generate_organisation_cache_information
    )
    inlines = [OrganisationLinkInline]
    form = OrganisationFormAdmin

    fieldsets = (
        (
            '',
            {
                'fields': (
                    'name', 'description', 'country', 'active'
                )
            },
        ),
        (
            'Licenses',
            {
                'fields': (
                    'license', 'restriction_code_type', 'constraints_other'
                )
            },
        ),
        (
            'Metadata',
            {
                'fields': (
                    'data_is_from_api', 'data_date_start',
                    'data_date_end',
                    'data_is_groundwater_level',
                    'data_is_groundwater_quality'
                )
            }
        ),
        (
            'Cache',
            {
                'fields': (
                    'data_cache_generated_at',
                )
            }
        )
    )
    readonly_fields = ('data_cache_generated_at',)

    def links(self, org: Organisation):
        return list(
            org.links.values_list('url', flat=True)
        )

    def _groups(self, org: Organisation):
        groups = list(
            OrganisationGroup.objects.filter(
                organisations__in=[org]
            ).values_list('name', flat=True)
        )
        if not len(groups):
            return '-'
        return groups

    def license_name(self, org: Organisation):
        """Return license name."""
        license = org.license_data
        if license:
            return license.name
        return '-'

    def data_cache_info(self, obj):
        if not obj.data_cache_information:
            return "-"
        try:
            single_line = json.dumps(obj.data_cache_information)
            return format_html(
                f"<div style='white-space: nowrap'>"
                f"{single_line.replace('{', '').replace('}', '')}"
                f"</div>"
            )
        except Exception as e:
            print(e)
            return str(obj.data_cache_information)

    data_cache_info.short_description = "Data cache information"


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
