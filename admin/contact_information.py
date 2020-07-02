from django.contrib import admin
from gwml2.models.contact_information import (
    CIResponsibleParty, CIOnlineResource, CIAddress,
    CITelephone, CIOnlineFunctionTerm, CIContact, CIRoleTerm
)


class CIContactAdmin(admin.ModelAdmin):
    list_display = (
        'phone', 'address', 'online_resource',
        'hours_of_service', 'contact_instruction')


class CITelephoneAdmin(admin.ModelAdmin):
    list_display = (
        'voice', 'facsimile')


class CIAddressAdmin(admin.ModelAdmin):
    list_display = (
        'delivery_point', 'city', 'administrative_area',
        'postal_code', 'country', 'electronic_mail_address')


class CIOnlineResourceAdmin(admin.ModelAdmin):
    list_display = (
        'linkage', 'protocol',
        'application_profile', 'name', 'description')


class CIResponsiblePartyAdmin(admin.ModelAdmin):
    list_display = (
        'individual_name', 'organisation_name', 'position_name')


admin.site.register(CIOnlineFunctionTerm)
admin.site.register(CIRoleTerm)
admin.site.register(CIContact, CIContactAdmin)
admin.site.register(CITelephone, CITelephoneAdmin)
admin.site.register(CIAddress, CIAddressAdmin)
admin.site.register(CIOnlineResource, CIOnlineResourceAdmin)
admin.site.register(CIResponsibleParty, CIResponsiblePartyAdmin)
