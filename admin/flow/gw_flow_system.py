from django.contrib import admin
from gwml2.models.flow.gw_flow import GWFlow
from gwml2.models.flow.gw_flow_system import GWFlowSystem


class GWFlowInline(admin.TabularInline):
    model = GWFlow


class Admin(admin.ModelAdmin):
    inlines = [GWFlowInline, ]


admin.site.register(GWFlowSystem, Admin)
