from django.contrib import admin
from gwml2.models.spring.gw_spring import GWSpring, GWStringType, SpringCauseType, SpringPersistenceType


admin.site.register(GWSpring)
admin.site.register(GWStringType)
admin.site.register(SpringPersistenceType)
admin.site.register(SpringCauseType)
