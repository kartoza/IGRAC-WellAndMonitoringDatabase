from django.contrib import admin
from gwml2.models.observations_measurements import OMProcess, OMObservation, NamedValue

admin.site.register(OMProcess)
admin.site.register(OMObservation)
admin.site.register(NamedValue)
