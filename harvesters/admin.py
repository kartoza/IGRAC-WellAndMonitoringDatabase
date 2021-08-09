from django import forms
from django.contrib import admin
from gwml2.harvesters.models.harvester import (
    Harvester, HarvesterAttribute, HarvesterLog, HarvesterWellData)
from gwml2.tasks.harvester import run_harvester

HYDAPI = 'gwml2.harvesters.harvester.hydapi.Hydapi'
HARVESTERS = (
    (HYDAPI, HYDAPI),
)


class HarvesterAttributeInline(admin.TabularInline):
    model = HarvesterAttribute
    readonly_fields = ('harvester', 'name')
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False


class HarvesterLogInline(admin.TabularInline):
    model = HarvesterLog
    readonly_fields = ('harvester', 'start_time', 'end_time', 'status', 'note')
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False


class HarvesterWellDataInline(admin.TabularInline):
    model = HarvesterWellData
    readonly_fields = ('well', 'measurements_found', 'from_time_data', 'to_time_data')
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False


class HarvesterForm(forms.ModelForm):
    harvester_class = forms.ChoiceField(choices=HARVESTERS)

    class Meta:
        model = Harvester
        fields = '__all__'


def harvest_data(modeladmin, request, queryset):
    for harvester in queryset:
        run_harvester.delay(harvester.id)


harvest_data.short_description = 'Harvest data of the harvester'


class HarvesterAdmin(admin.ModelAdmin):
    form = HarvesterForm
    inlines = [HarvesterAttributeInline, HarvesterLogInline, HarvesterWellDataInline]
    list_display = ('name', 'organisation', 'is_run', 'active', 'harvester_class')
    readonly_fields = ('is_run',)
    list_editable = ('active',)
    actions = (harvest_data,)


admin.site.register(Harvester, HarvesterAdmin)
