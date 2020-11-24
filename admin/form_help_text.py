from django.contrib import admin
from gwml2.models.form_help_text import FormHelpText


class FormHelpTextAdmin(admin.ModelAdmin):
    list_display = ('form', 'field', 'help_text')
    list_filter = ('form',)
    search_fields = ('field',)


admin.site.register(FormHelpText, FormHelpTextAdmin)
