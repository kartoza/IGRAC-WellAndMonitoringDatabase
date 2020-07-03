from django.contrib import admin
from gwml2.models.hydrogeological_unit.gw_confining_bed import (
    SpatialConfinementTypeTerm, ConductivityConfinementTypeTerm, GWConfiningBed)

admin.site.register(SpatialConfinementTypeTerm)
admin.site.register(ConductivityConfinementTypeTerm)
admin.site.register(GWConfiningBed)
