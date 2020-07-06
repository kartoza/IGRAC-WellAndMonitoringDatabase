from django.contrib import admin
from gwml2.models.spring.gw_spring import GWSpring, SpringType, SpringCauseType, SpringPersistenceType


admin.site.register(GWSpring)
admin.site.register(SpringType)
admin.site.register(SpringPersistenceType)
admin.site.register(SpringCauseType)
