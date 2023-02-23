from django import forms
from django.contrib import admin

from gwml2.harvesters.models.harvester import (
    Harvester, HarvesterAttribute, HarvesterLog, HarvesterWellData)
from gwml2.tasks.harvester import run_harvester

# Argentine
AZULBHD = (
    'gwml2.harvesters.harvester.azul_bdh.AzulBdh',
    '(Argentine) Institute of Plains Hydrology - IHLLA '
    '(http://www.azul.bdh.org.ar/bdh3/leaflet/index.html)',
    None
)

# Canada
GINGWINFO = (
    'gwml2.harvesters.harvester.gin_gw_info.GinGWInfo',
    '(Canada) Canadian Groundwater Information (https://gin.gw-info.net/)',
    'Geological Survey Canada (Canada)'
)

# France
HUBEAU = (
    'gwml2.harvesters.harvester.hubeau.Hubeau',
    '(France) French Geological Survey '
    '(https://hubeau.eaufrance.fr/page/api-piezometrie)',
    'French Geological Survey (France)'
)

# Ireland
EPAWEBAPP = (
    'gwml2.harvesters.harvester.epawebapp.Epawebapp',
    '(Ireland) Groundwater in Ireland '
    '(https://epawebapp.epa.ie/hydronet/#Groundwater)',
    None
)

# New Zealand
GNSCRI = (
    'gwml2.harvesters.harvester.gns_cri.GnsCri',
    '(New Zealand) GNS Science, Te Pū Ao '
    '(https://data.gns.cri.nz/)',
    'GNS Science, Te Pū Ao (New Zealand)'
)

# Norway
HYDAPI = (
    'gwml2.harvesters.harvester.hydapi.Hydapi',
    '(Norway) The Norwegian Water Resources and Energy Directorate '
    '(https://hydapi.nve.no/)',
    'Norwegian Water Resources and Energy Directorate NVE (Norway)'
)

# Sweden
SGUAPI = (
    'gwml2.harvesters.harvester.sgu.SguAPI',
    '(Sweden) Groundwater in Sweden '
    '(https://apps.sgu.se/grundvattennivaer-rest/stationer)',
    'Geological Survey of Sweden (Sweden)'
)

# USA
CIDA_USGS = (
    'gwml2.harvesters.harvester.cida.CidaUsgs',
    '(United States) National Ground-Water Monitoring Network (United States) '
    '(https://cida.usgs.gov/ngwmn/index.jsp)',
    None
)

# EHYD
EHYD = (
    'gwml2.harvesters.harvester.ehyd.EHYD',
    '(Austria) Electronic Hydrographic Data '
    '(https://www.ehyd.gv.at/)',
    None
)

HARVESTERS = (
    AZULBHD,
    GINGWINFO,
    HUBEAU,
    EPAWEBAPP,
    GNSCRI,
    HYDAPI,
    SGUAPI,
    CIDA_USGS,
    EHYD
)
HARVESTERS_CHOICES = (
    (harvester[0], harvester[1]) for harvester in HARVESTERS
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
    harvester_class = forms.ChoiceField(choices=HARVESTERS_CHOICES)

    class Meta:
        model = Harvester
        exclude = ('public', 'downloadable')


def harvest_data(modeladmin, request, queryset):
    for harvester in queryset:
        run_harvester(harvester.id)


harvest_data.short_description = 'Harvest data of the harvester'


class HarvesterAdmin(admin.ModelAdmin):
    form = HarvesterForm
    inlines = [HarvesterAttributeInline, HarvesterLogInline]
    list_display = (
        'id', 'name', 'organisation', 'is_run', 'active', 'harvester_class', 'last_run')
    list_editable = ('active',)
    actions = (harvest_data,)

    def last_run(self, obj: Harvester):
        last_log = obj.harvesterlog_set.first()
        if not last_log:
            return '-'
        return last_log.start_time


class HarvesterWellDataAdmin(admin.ModelAdmin):
    list_display = (
        'harvester', 'well', 'measurements_found', 'from_time_data',
        'to_time_data')
    readonly_fields = (
        'well', 'measurements_found', 'from_time_data', 'to_time_data')
    list_filter = ('harvester',)


admin.site.register(Harvester, HarvesterAdmin)
admin.site.register(HarvesterWellData, HarvesterWellDataAdmin)
