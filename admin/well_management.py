from django.contrib import admin
from django.contrib.auth import get_user_model

from gwml2.forms.organisation import OrganisationFormAdmin
from gwml2.models.well_management.organisation import (
    Organisation, OrganisationType
)
from gwml2.models.well_management.user import UserUUID
from gwml2.utils.management_commands import run_command

User = get_user_model()


def reassign_wells_country(modeladmin, request, queryset):
    for org in queryset.filter(country__isnull=False):
        org.well_set.all().update(country=org.country)


@admin.action(description='Generate data cache')
def generate_data_wells_cache(modeladmin, request, queryset):
    """Generate measurement cache."""
    ids = [f'{_id}' for _id in queryset.values_list('id', flat=True)]
    return run_command(
        request,
        'generate_data_organisations_cache',
        args=[
            "--ids", ', '.join(ids), "--force"
        ]
    )


class OrganisationAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'active', 'country', 'well_number', 'data_cache_generated_at'
    )
    list_editable = ('active',)
    list_filter = ('data_cache_generated_at', 'country')
    actions = (generate_data_wells_cache, reassign_wells_country)
    form = OrganisationFormAdmin

    def well_number(self, org: Organisation):
        return org.well_set.all().count()


def fetch(modeladmin, request, queryset):
    for user in User.objects.exclude(
            id__in=list(UserUUID.objects.values_list('user_id', flat=True))):
        UserUUID.objects.get_or_create(user_id=user.id)


fetch.short_description = "Create uuid for other users"


def update_username(modeladmin, request, queryset):
    for query in queryset:
        query.update_username()


update_username.short_description = "Update username"


class UserUUIDAdmin(admin.ModelAdmin):
    list_display = ('user', 'uuid', 'username')
    actions = [fetch, update_username]

    def user(self, obj):
        try:
            return User.objects.get(id=obj.user_id).username
        except User.DoesNotExist:
            return '-'


admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(OrganisationType, admin.ModelAdmin)
