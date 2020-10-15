from django.contrib import admin
from gwml2.models.reference_elevation import ReferenceElevation
from gwml2.models.reference_elevation import ReferenceElevationType

admin.site.register(ReferenceElevationType)
admin.site.register(ReferenceElevation)
