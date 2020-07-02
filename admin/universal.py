from django.contrib import admin
from gwml2.models.universal import Quantity


class QuantityAdmin(admin.ModelAdmin):
    list_display = ('unit', 'value')


admin.site.register(Quantity, QuantityAdmin)
