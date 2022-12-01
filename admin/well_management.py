from django.contrib import admin
from django.contrib.auth import get_user_model

from gwml2.forms.organisation import OrganisationFormAdmin
from gwml2.models.well_management.organisation import (
    Organisation, OrganisationType
)
from gwml2.models.well_management.user import UserUUID
from gwml2.tasks.data_file_cache.country_recache import (
    generate_data_country_cache
)

User = get_user_model()


def rerun_cache(modeladmin, request, queryset):
    for org in queryset:
        codes = list(set(org.well_set.values_list('country__code', flat=True)))
        for country_code in codes:
            generate_data_country_cache(country_code=country_code)


class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('name', 'active')
    list_editable = ('active',)
    actions = (rerun_cache,)
    form = OrganisationFormAdmin


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
