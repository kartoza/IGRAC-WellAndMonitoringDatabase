from django.contrib import admin
from gwml2.models.flow.gw_water_budget import GWWaterBudget


class Admin(admin.ModelAdmin):
    list_display = ('gw_budget_amount', 'gw_budget_valid_time')


admin.site.register(GWWaterBudget, Admin)
