from django import forms
from django.contrib import admin

from gwml2.harvesters.models.harvester import (
    Harvester, HarvesterAttribute, HarvesterParameterMap,
    HarvesterLog, HarvesterWellData
)
from gwml2.models.site_preference import SitePreference
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

# USA
CIDA_USGS = (
    'gwml2.harvesters.harvester.cida.CidaUsgs',
    '(United States) National Ground-Water Monitoring Network (United States) '
    '(https://cida.usgs.gov/ngwmn/index.jsp)',
    None
)

# ---------------------------------------------
# AUSTRIA (EHYD)
# ---------------------------------------------
EHYD = (
    'gwml2.harvesters.harvester.ehyd.FileBase',
    '(Austria) Electronic Hydrographic Data '
    '(https://www.ehyd.gv.at/)',
    None
)

# ---------------------------------------------
# FRANCE (HUBEAU)
# ---------------------------------------------
HUBEAU_WATER_LEVEL = (
    'gwml2.harvesters.harvester.hubeau.level.HubeauWaterLevel',
    '(France) Water Level in France '
    '(https://hubeau.eaufrance.fr/page/api-piezometrie)',
    'French Geological Survey (France)'
)
HUBEAU_WATER_QUALITY = (
    'gwml2.harvesters.harvester.hubeau.quality.HubeauWaterQuality',
    '(France) Water Quality in France '
    '(https://hubeau.eaufrance.fr/page/api-qualite-nappes)',
    'French Geological Survey (France)'
)

# ---------------------------------------------
# Sweden (SGU)
# ---------------------------------------------
SGU_GROUNDWATER_API = (
    'gwml2.harvesters.harvester.sgu.water_level.SguWaterLevelAPI',
    '(Sweden) Water level in Sweden '
    '(https://apps.sgu.se/grundvattennivaer-rest/stationer)',
    'Geological Survey of Sweden (Sweden)'
)

SGU_QUALITY_API = (
    'gwml2.harvesters.harvester.sgu.quality.SguQualityAPI',
    '(Sweden) Quality in Sweden '
    '(https://www.sgu.se/grundvatten/miljoovervakning-av-grundvatten/kartvisare-och-diagram-for-miljoovervakning-av-grundvattenkemi/)',
    'Geological Survey of Sweden (Sweden)'
)

SGU_SPRINGS_API = (
    'gwml2.harvesters.harvester.sgu.spring.SguSpringAPI',
    '(Sweden) Spring in Sweden '
    '(https://apps.sgu.se/kartvisare/kartvisare-kallor.html)',
    'Geological Survey of Sweden (Sweden)'
)

HARVESTERS = (
    AZULBHD,
    EHYD,
    GINGWINFO,
    HUBEAU_WATER_LEVEL,
    HUBEAU_WATER_QUALITY,
    EPAWEBAPP,
    GNSCRI,
    HYDAPI,
    SGU_GROUNDWATER_API,
    SGU_QUALITY_API,
    SGU_SPRINGS_API,
    CIDA_USGS,
)
HARVESTERS_CHOICES = (
    (harvester[0], harvester[1]) for harvester in HARVESTERS
)


class HarvesterAttributeInline(admin.TabularInline):
    model = HarvesterAttribute
    readonly_fields = ('harvester',)
    extra = 0


class HarvesterParameterMapInline(admin.TabularInline):
    model = HarvesterParameterMap
    readonly_fields = ('harvester',)
    extra = 0
    ordering = ['key']


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
        run_harvester.delay(harvester.id)


harvest_data.short_description = 'Run'


class HarvesterAdmin(admin.ModelAdmin):
    """Admin for Harvester model."""
    form = HarvesterForm
    inlines = [
        HarvesterAttributeInline, HarvesterParameterMapInline,
        HarvesterLogInline
    ]
    list_display = (
        'id', 'name', 'organisation', 'is_run', 'active', 'harvester_class',
        'last_run', 'task_id', 'task_status', 'last_log'
    )
    list_editable = ('active',)
    actions = (harvest_data,)
    ordering = ['name']

    def last_run(self, obj: Harvester):
        """Return last run time."""
        return obj.last_run

    def task_status(self, obj: Harvester):
        """If status is running on celery."""
        pref = SitePreference.load()
        try:
            pref.running_harvesters.get(id=obj.id)
            return 'RUNNING'
        except pref.running_harvesters.model.DoesNotExist:
            return None

    def last_log(self, obj: Harvester):
        """Return last log."""
        log = obj.harvesterlog_set.first()
        if not log:
            return '-'
        return f'{log.status} : {log.note}'


class HarvesterWellDataAdmin(admin.ModelAdmin):
    list_display = (
        'harvester', 'well', 'measurements_found', 'from_time_data',
        'to_time_data')
    readonly_fields = (
        'well', 'measurements_found', 'from_time_data', 'to_time_data')
    list_filter = ('harvester',)


admin.site.register(Harvester, HarvesterAdmin)
admin.site.register(HarvesterWellData, HarvesterWellDataAdmin)
