from django.contrib import admin
from gwml2.models.construction import Construction, Casing, Screen


class CasingInline(admin.TabularInline):
    model = Casing


class ScreenInline(admin.TabularInline):
    model = Screen


class ConstructionAdmin(admin.ModelAdmin):
    inlines = [CasingInline, ScreenInline]


admin.site.register(Construction, ConstructionAdmin)
