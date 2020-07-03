from django.contrib import admin
from gwml2.models.hydrogeological_unit.gw_aquifer import GWAquifer, AquiferTypeTerm

admin.site.register(AquiferTypeTerm)
admin.site.register(GWAquifer)
