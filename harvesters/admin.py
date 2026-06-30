import csv

from django import forms
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path as url_path, reverse
from django.utils.html import format_html

from gwml2.harvesters.models.harvester import (
    Harvester, HarvesterAttribute, HarvesterParameterMap, HarvesterLog
)
from gwml2.models.site_preference import SitePreference
from gwml2.tasks.harvester import run_harvester

# Argentine
AZULBHD = (
    'gwml2.harvesters.harvester.azul_bdh.AzulBdh',
    '(Argentine) Institute of Plains Hydrology - IHLLA',
    None
)

# Canada
GINGWINFO = (
    'gwml2.harvesters.harvester.gin_gw_info.GinGWInfo',
    '(Canada) Canadian Groundwater Information',
    'Geological Survey Canada (Canada)'
)

# Estonia
ESTONIA = (
    'gwml2.harvesters.harvester.keskkonnaportaal_estonia.harvester.KeskkonnaportaalEstoniaHarvester',
    '(Estonia) Level and Quality Data',
    'Estonia - Geological Survey of Estonia'
)

# Ireland
EPAWEBAPP = (
    'gwml2.harvesters.harvester.epawebapp.Epawebapp',
    '(Ireland) Groundwater in Ireland',
    None
)

# New Zealand
GNSCRI = (
    'gwml2.harvesters.harvester.gns_cri.GnsCri',
    '(New Zealand) GNS Science, Te Pū Ao ',
    'GNS Science, Te Pū Ao (New Zealand)'
)

# Norway
HYDAPI = (
    'gwml2.harvesters.harvester.hydapi.Hydapi',
    '(Norway) The Norwegian Water Resources and Energy Directorate ',
    'Norwegian Water Resources and Energy Directorate NVE (Norway)'
)

# RWANDA
RWANDA = (
    'gwml2.harvesters.harvester.rwanda.base.RwandaHarvester',
    '(Rwanda) Rwanda Water Portal ',
    'Rwanda - Rwanda Water Resources Board (RWB)'
)

# ------------------------------------------
# USA (CIDA)
# ------------------------------------------
CIDA_USGS_WATER_LEVEL = (
    'gwml2.harvesters.harvester.cida.level.CidaUsgsWaterLevel',
    '(United States) National Ground-Water Monitoring Network - Water Level ',
    None
)
CIDA_USGS_WATER_QUALITY = (
    'gwml2.harvesters.harvester.cida.quality.CidaUsgsWaterQuality',
    '(United States) National Ground-Water Monitoring Network - Water Quality ',
    None
)
# ------------------------------------------
# NETHERLAND
# ------------------------------------------
NETHERLAND_WATER_LEVEL = (
    'gwml2.harvesters.harvester.netherland.level.NetherlandLevelHarvester',
    '(Netherland) Level measurements in Netherland',
    None
)
NETHERLAND_QUALITY = (
    'gwml2.harvesters.harvester.netherland.quality.NetherlandQualityHarvester',
    '(Netherland) Quality measurements in Netherland',
    None
)

# ---------------------------------------------
# AUSTRIA (EHYD)
# ---------------------------------------------
EHYD = (
    'gwml2.harvesters.harvester.ehyd.FileBase',
    '(Austria) Electronic Hydrographic Data',
    None
)

# ---------------------------------------------
# FRANCE (HUBEAU)
# ---------------------------------------------
HUBEAU_WATER_LEVEL = (
    'gwml2.harvesters.harvester.hubeau.level.HubeauWaterLevel',
    '(France) Water Level in France',
    'French Geological Survey (France)'
)
HUBEAU_WATER_QUALITY = (
    'gwml2.harvesters.harvester.hubeau.quality.HubeauWaterQuality',
    '(France) Water Quality in France',
    'French Geological Survey (France)'
)

# ---------------------------------------------
# Sweden (SGU)
# ---------------------------------------------
SGU_GROUNDWATER_API = (
    'gwml2.harvesters.harvester.sgu.water_level.SguWaterLevelAPI',
    '(Sweden) Water level in Sweden',
    'Geological Survey of Sweden (Sweden)'
)

SGU_QUALITY_API = (
    'gwml2.harvesters.harvester.sgu.quality.SguQualityAPI',
    '(Sweden) Quality in Sweden',
    'Geological Survey of Sweden (Sweden)'
)

SGU_SPRINGS_API = (
    'gwml2.harvesters.harvester.sgu.spring.SguSpringAPI',
    '(Sweden) Spring in Sweden',
    'Geological Survey of Sweden (Sweden)'
)

# ---------------------------------------------
# LOWER SAXONY
# ---------------------------------------------
LOWER_SAXONY_LEVEL_MEASUREMENTS = (
    'gwml2.harvesters.harvester.lower_saxony.LowerSaxonyHarvester',
    '(Lower Saxony) Level measurements',
    None
)

# ---------------------------------------------
# NORWAY QUALITY (MILJODIREKTORATET)
# ---------------------------------------------
NORWAY_QUALITY = (
    'gwml2.harvesters.harvester.miljodirektoratet.MiljodirektoratetHarvester',
    '(Norway Quality) Quality measurements',
    None
)

# ---------------------------------------------
# EL SAVADOR
# ---------------------------------------------
EL_SAVADOR = (
    'gwml2.harvesters.harvester.el_savador.base.ElSavadorHarvester',
    (
        '(El Savador) General Directorate of '
        'the Observatory of Threats and Natural Resources'
    ),
    None
)

HARVESTERS = (
    AZULBHD,
    EHYD,
    GINGWINFO,
    EL_SAVADOR,
    ESTONIA,
    HUBEAU_WATER_LEVEL,
    HUBEAU_WATER_QUALITY,
    EPAWEBAPP,
    LOWER_SAXONY_LEVEL_MEASUREMENTS,
    RWANDA,
    NETHERLAND_WATER_LEVEL,
    NETHERLAND_QUALITY,
    GNSCRI,
    NORWAY_QUALITY,
    HYDAPI,
    SGU_GROUNDWATER_API,
    SGU_QUALITY_API,
    SGU_SPRINGS_API,
    CIDA_USGS_WATER_LEVEL,
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
    readonly_fields = (
        'harvester', 'start_time', 'end_time', 'status', 'note',
        'download_well_progress'
    )
    exclude = ('well_progress',)
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def download_well_progress(self, obj):
        if not obj.pk or not obj.well_progress:
            return '-'
        url = reverse('admin:harvesterlog_well_progress_csv', args=[obj.pk])
        return format_html('<a href="{}">Download CSV</a>', url)

    download_well_progress.short_description = 'Well Progress'


class HarvesterForm(forms.ModelForm):
    harvester_class = forms.ChoiceField(choices=HARVESTERS_CHOICES)

    class Meta:
        model = Harvester
        exclude = ('public', 'downloadable')


def harvest_data(modeladmin, request, queryset):
    for harvester in queryset:
        run_harvester.delay(harvester.id)


harvest_data.short_description = 'Run'


@admin.register(Harvester)
class HarvesterAdmin(admin.ModelAdmin):
    """Admin for Harvester model."""
    form = HarvesterForm
    inlines = [
        HarvesterAttributeInline, HarvesterParameterMapInline,
        HarvesterLogInline
    ]
    list_display = (
        'id', 'name', 'organisation', 'save_missing_well', 'is_run', 'active',
        'harvester_class',
        'last_run', 'task_id', 'task_status', 'last_log'
    )
    list_editable = ('active',)
    actions = (harvest_data,)
    ordering = ['name']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            url_path(
                'log/<int:log_id>/well_progress.csv/',
                self.admin_site.admin_view(self.well_progress_csv_view),
                name='harvesterlog_well_progress_csv'
            ),
        ]
        return custom_urls + urls

    def well_progress_csv_view(self, request, log_id):
        log = HarvesterLog.objects.get(pk=log_id)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            f'attachment; filename="well_progress_{log_id}.csv"'
        )
        writer = csv.writer(response)
        writer.writerow(['id', 'status', 'note'])
        for entry in log.well_progress:
            writer.writerow([
                entry.get('id', ''),
                entry.get('status', ''),
                entry.get('note', ''),
            ])
        return response

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
