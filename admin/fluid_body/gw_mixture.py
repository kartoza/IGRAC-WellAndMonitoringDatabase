from django.contrib import admin
from gwml2.models.fluid_body.gw_mixture import *


class GWMixtureConstituentAdmin(admin.ModelAdmin):
    list_display = ('gw_mixture', 'gw_constituent')


admin.site.register(MixtureType)
admin.site.register(GWMixture)
admin.site.register(GWMixtureConstituent, GWMixtureConstituentAdmin)
