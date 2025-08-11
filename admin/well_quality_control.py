from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from gwml2.models.well_management.organisation import Organisation, Country
from gwml2.models.well_quality_control import WellQualityControl


class OrganisationFilter(admin.SimpleListFilter):
    title = 'Organisation'
    parameter_name = 'organisation'

    def lookups(self, request, model_admin):
        """Return a list of tuples (value, label) for the filter dropdown."""
        return [
            (a.id, a.name) for a in Organisation.objects.all()
        ]

    def queryset(self, request, queryset):
        """Filter queryset based on the selected value."""
        if self.value():
            return queryset.filter(well__organisation_id=self.value())
        return queryset


class CountryFilter(admin.SimpleListFilter):
    title = 'Country'
    parameter_name = 'country'

    def lookups(self, request, model_admin):
        """Return a list of tuples (value, label) for the filter dropdown."""
        return [
            (a.id, a.name) for a in Country.objects.all()
        ]

    def queryset(self, request, queryset):
        """Filter queryset based on the selected value."""
        if self.value():
            return queryset.filter(well__country_id=self.value())
        return queryset


class TimeGapQualityFilter(admin.SimpleListFilter):
    """Quality filter."""

    title = 'Has good time gap quality?'
    parameter_name = 'is_groundwater_level_time_gap_quality'

    def lookups(self, request, model_admin):
        """Lookup function for entity filter."""
        return [
            ("yes", "Yes"),
            ("no", "No"),
        ]

    def queryset(self, request, queryset):
        """Return filtered queryset."""
        if self.value() == "yes":
            return queryset.filter(groundwater_level_time_gap__isnull=True)
        if self.value() == "no":
            return queryset.filter(groundwater_level_time_gap__isnull=False)
        return queryset


class ValueGapQualityFilter(admin.SimpleListFilter):
    """Quality filter."""

    title = 'Has good value gap quality?'
    parameter_name = 'is_groundwater_level_value_gap_quality'

    def lookups(self, request, model_admin):
        """Lookup function for entity filter."""
        return [
            ("yes", "Yes"),
            ("no", "No"),
        ]

    def queryset(self, request, queryset):
        """Return filtered queryset."""
        if self.value() == "yes":
            return queryset.filter(groundwater_level_value_gap__isnull=True)
        if self.value() == "no":
            return queryset.filter(groundwater_level_value_gap__isnull=False)
        return queryset


class ValueStrangeQualityFilter(admin.SimpleListFilter):
    """Quality filter."""

    title = "Don't have strange value?"
    parameter_name = 'is_groundwater_level_strange_value_quality'

    def lookups(self, request, model_admin):
        """Lookup function for entity filter."""
        return [
            ("yes", "Yes"),
            ("no", "No"),
        ]

    def queryset(self, request, queryset):
        """Return filtered queryset."""
        if self.value() == "yes":
            return queryset.filter(
                groundwater_level_strange_value__isnull=True
            )
        if self.value() == "no":
            return queryset.filter(
                groundwater_level_strange_value__isnull=False
            )
        return queryset


@admin.register(WellQualityControl)
class WellQualityControlAdmin(admin.ModelAdmin):
    list_display = (
        'well',
        # 'organisation',
        # 'country',
        '_groundwater_level_time_gap_quality',
        'groundwater_level_time_gap_generated_time',
        '_groundwater_level_value_gap_quality',
        'groundwater_level_value_gap_generated_time',
        '_groundwater_level_strange_value_quality',
        'groundwater_level_strange_value_generated_time',
        'edit'
    )
    list_filter = (
        OrganisationFilter, CountryFilter,
        TimeGapQualityFilter, ValueGapQualityFilter, ValueStrangeQualityFilter
    )

    def edit(self, obj: WellQualityControl):
        url = reverse('well_form', args=[obj.well.id])
        return format_html(
            '<a href="{}" target="_blank">Edit well</a>',
            url
        )

    def _groundwater_level_time_gap_quality(self, obj: WellQualityControl):
        """Return groundwater level time gap."""
        return obj.groundwater_level_time_gap is None

    _groundwater_level_time_gap_quality.boolean = True

    def _groundwater_level_value_gap_quality(self, obj: WellQualityControl):
        """Return groundwater level time gap."""
        return obj.groundwater_level_value_gap is None

    _groundwater_level_value_gap_quality.boolean = True

    def _groundwater_level_strange_value_quality(
            self, obj: WellQualityControl
    ):
        """Return groundwater level time gap."""
        return obj.groundwater_level_strange_value is None

    _groundwater_level_strange_value_quality.boolean = True
