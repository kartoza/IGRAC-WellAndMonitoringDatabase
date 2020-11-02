from django.contrib import admin
from gwml2.models.well_management.organisation import Organisation
from gwml2.forms.organisation import OrganisationForm


class OrganisationAdmin(admin.ModelAdmin):
    form = OrganisationForm


admin.site.register(Organisation, OrganisationAdmin)
