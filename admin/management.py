from django.contrib import admin
from gwml2.models.management import Management, License


class LicenseAdmin(admin.ModelAdmin):
    list_display = ('number', 'valid_from', 'valid_until')


class ManagementAdmin(admin.ModelAdmin):
    list_display = ('manager', 'license')


admin.site.register(License, LicenseAdmin)
admin.site.register(Management, ManagementAdmin)
