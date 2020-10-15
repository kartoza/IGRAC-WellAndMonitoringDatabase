from django.contrib import admin
from gwml2.models.term import (
    TermAquiferType, TermConfinement, TermDrillingMethod, TermWellPurpose, TermWellStatus,
    TermFeatureType, TermGroundwaterUse, TermMeasurementParameter
)

admin.site.register(TermAquiferType)
admin.site.register(TermConfinement)
admin.site.register(TermDrillingMethod)
admin.site.register(TermFeatureType)
admin.site.register(TermGroundwaterUse)
admin.site.register(TermMeasurementParameter)
admin.site.register(TermWellPurpose)
admin.site.register(TermWellStatus)
