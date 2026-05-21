import json

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.urls import path
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


@admin.action(description='Generate measurement stats')
def generate_measurement_stats(modeladmin, request, queryset):
    """Generate missing stats keys only; skip keys that already have a value."""
    from gwml2.tasks.organisation import generate_measurement_stats as task
    for org in queryset:
        task.delay(org.id, force=False)


@admin.action(description='Force generate measurement stats')
def force_generate_measurement_stats(modeladmin, request, queryset):
    """Recompute all stats keys regardless of existing values."""
    from gwml2.tasks.organisation import generate_measurement_stats as task
    for org in queryset:
        task.delay(org.id, force=True)


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
        'license_name', 'active', 'country', '_groups',
        'measurement_stats_generated_at',
        'data_cache_generated_at', 'data_cache_info',
        'measurement_links', 'measurement_stats_display',
        'description', 'links'
    )
    change_list_template = 'admin/organisation_change_list.html'
    list_editable = ('active',)
    list_filter = ('data_cache_generated_at', 'country')
    search_fields = ('name',)
    show_full_result_count = False
    actions = (
        generate_data_wells_cache, reassign_wells_country, update_ggis_uid,
        assign_data_types, assign_date_range, assign_license,
        generate_organisation_cache_information,
        generate_measurement_stats, force_generate_measurement_stats,
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
    readonly_fields = ('data_cache_generated_at',
                       'measurement_stats_generated_at')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'country'
        ).prefetch_related(
            'links',
            'groups',
        )

    def changelist_view(self, request, extra_context=None):
        # Cache all License names in one query instead of one per row
        try:
            from geonode.base.models import License
            self._license_cache = {
                lic.id: lic.name for lic in License.objects.all()
            }
        except Exception:
            self._license_cache = {}
        return super().changelist_view(request, extra_context=extra_context)

    def links(self, org: Organisation):
        return [link.url for link in org.links.all()]

    def measurement_links(self, org: Organisation):
        base = f'organisation={org.id}'
        return format_html(
            '<a href="/admin/gwml2/welllevelmeasurement/?{q}" target="_blank">Level</a> | '
            '<a href="/admin/gwml2/wellqualitymeasurement/?{q}" target="_blank">Quality</a> | '
            '<a href="/admin/gwml2/wellyieldmeasurement/?{q}" target="_blank">Yield</a>',
            q=base,
        )

    measurement_links.short_description = 'Measurements'

    def _groups(self, org: Organisation):
        groups = [g.name for g in org.groups.all()]
        return groups if groups else '-'

    def license_name(self, org: Organisation):
        if not org.license:
            return '-'
        cache = getattr(self, '_license_cache', None)
        if cache is not None:
            return cache.get(org.license, '-')
        return org.license_data.name if org.license_data else '-'

    def get_urls(self):
        custom = [
            path(
                'totals/',
                self.admin_site.admin_view(self.totals_view),
                name='gwml2_organisation_totals',
            ),
        ]
        return custom + super().get_urls()

    def totals_view(self, request):
        from django.db.models.expressions import RawSQL
        from django.db.models import Sum
        qs = self.get_queryset(request).filter(
            measurement_stats__isnull=False
        )
        keys = [
            'total', 'total_level', 'total_quality', 'total_yield',
            'midnight_level', 'midnight_quality', 'midnight_yield',
        ]
        agg = qs.aggregate(**{
            k: Sum(RawSQL(f"(measurement_stats->>'{k}')::int", []))
            for k in keys
        })
        return JsonResponse({k: v or 0 for k, v in agg.items()})

    def measurement_stats_display(self, org: Organisation):
        stats = org.measurement_stats
        if not stats:
            return '-'

        def fmt(key):
            v = stats.get(key)
            return f'{v:,}' if isinstance(v, int) else '-'

        lines = [
            f"Total: {fmt('total')}",
            f"Level: {fmt('total_level')}",
            f"Quality: {fmt('total_quality')}",
            f"Yield: {fmt('total_yield')}",
            f"Midnight L: {fmt('midnight_level')}",
            f"Midnight Q: {fmt('midnight_quality')}",
            f"Midnight Y: {fmt('midnight_yield')}",
        ]
        return format_html(
            '<div style="white-space:nowrap">{}</div>',
            format_html('<br>'.join(lines))
        )

    measurement_stats_display.short_description = 'Measurement Stats'

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
