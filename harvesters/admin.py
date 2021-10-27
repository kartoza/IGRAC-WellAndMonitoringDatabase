from django import forms
from django.contrib import admin
from gwml2.harvesters.models.harvester import (
    Harvester, HarvesterAttribute, HarvesterLog, HarvesterWellData)
from gwml2.tasks.harvester import run_harvester

HYDAPI = 'gwml2.harvesters.harvester.hydapi.Hydapi'
SGUAPI = 'gwml2.harvesters.harvester.sgu.SguAPI'
GINGWINFO = 'gwml2.harvesters.harvester.gin_gw_info.GinGWInfo'
HARVESTERS = (
    (HYDAPI, HYDAPI),
    (SGUAPI, SGUAPI),
    (GINGWINFO, GINGWINFO),
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


class HarvesterForm(forms.ModelForm):
    harvester_class = forms.ChoiceField(choices=HARVESTERS)

    class Meta:
        model = Harvester
        fields = '__all__'


def harvest_data(modeladmin, request, queryset):
    for harvester in queryset:
        run_harvester(harvester.id)


harvest_data.short_description = 'Harvest data of the harvester'


class HarvesterAdmin(admin.ModelAdmin):
    form = HarvesterForm
    inlines = [HarvesterAttributeInline, HarvesterLogInline]
    list_display = ('id', 'name', 'organisation', 'is_run', 'active', 'harvester_class')
    list_editable = ('active',)
    actions = (harvest_data,)


class HarvesterWellDataAdmin(admin.ModelAdmin):
    list_display = ('harvester', 'well', 'measurements_found', 'from_time_data', 'to_time_data')
    readonly_fields = ('well', 'measurements_found', 'from_time_data', 'to_time_data')
    list_filter = ('harvester',)


admin.site.register(Harvester, HarvesterAdmin)
admin.site.register(HarvesterWellData, HarvesterWellDataAdmin)
