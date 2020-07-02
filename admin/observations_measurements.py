from django.contrib import admin
from gwml2.models.observations_measurements import OMProcess, OMObservation
from gwml2.models.universal import NamedValue


class OMObservationAdmin(admin.ModelAdmin):
    filter_horizontal = ('parameter',)


class NamedValueAdmin(admin.ModelAdmin):
    list_display = ('name', 'value')


admin.site.register(OMProcess)
admin.site.register(OMObservation)
admin.site.register(NamedValue)
