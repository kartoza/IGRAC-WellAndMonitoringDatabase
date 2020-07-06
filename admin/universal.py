from django.contrib import admin
from gwml2.models.universal import (
    Quantity, PositionalAccuracyType, ElevationMeasurementMethodType,
    ElevationTypeTerm, Elevation, DocumentCitation, NamedValue, TemporalType)


class QuantityAdmin(admin.ModelAdmin):
    list_display = ('unit', 'value')


admin.site.register(Quantity, QuantityAdmin)
admin.site.register(PositionalAccuracyType)
admin.site.register(ElevationMeasurementMethodType)
admin.site.register(ElevationTypeTerm)
admin.site.register(Elevation)
admin.site.register(DocumentCitation)
admin.site.register(NamedValue)
admin.site.register(TemporalType)
