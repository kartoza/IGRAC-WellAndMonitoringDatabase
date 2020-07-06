from django.contrib import admin
from gwml2.models.flow.gw_flow import (
    GWFlow, FlowPersistenceType, WaterFlowProcess
)

admin.site.register(FlowPersistenceType)
admin.site.register(WaterFlowProcess)
admin.site.register(GWFlow)
