from django import forms
from gwml2.models.form_help_text import FormHelpText


class WellBaseForm(forms.ModelForm):
    """ contains global functions"""

    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        for field_name, field in self.fields.items():
            try:
                field.help_text = FormHelpText.objects.get(
                    form=self.__class__.__name__,
                    field=field_name
                ).help_text
            except FormHelpText.DoesNotExist:
                pass
