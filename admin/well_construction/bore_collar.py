from django.contrib import admin
from gwml2.models.well_construction.bore_collar import (
    CollarElevationTypeTerm, HeadworkTypeTerm, BoreCollar
)

admin.site.register(CollarElevationTypeTerm)
admin.site.register(HeadworkTypeTerm)
admin.site.register(BoreCollar)
