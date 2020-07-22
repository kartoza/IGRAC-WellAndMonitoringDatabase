from django import forms

MANAGEMENT_TYPE = (
    ('MANAGEMENT TYPE 1', 'MANAGEMENT TYPE 1'),
    ('MANAGEMENT TYPE 2', 'MANAGEMENT TYPE 2')
)


class OrganisationForm(forms.Form):
    """
    Form of Organisation
    """
    management_type = forms.ChoiceField(
        choices=MANAGEMENT_TYPE,
        widget=forms.Select())
    organisation = forms.CharField(required=False)
    owner = forms.CharField(required=False)
    responsible = forms.CharField(required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)
