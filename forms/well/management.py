from django import forms


MANAGEMENT_TYPE = (
    ('MANAGEMENT TYPE 1', 'MANAGEMENT TYPE 1'),
    ('MANAGEMENT TYPE 2', 'MANAGEMENT TYPE 2')
)


class ManagementForm(forms.Form):
    """Form for management."""

    management_type = forms.ChoiceField(
        choices=MANAGEMENT_TYPE,
        widget=forms.Select(),
        required=True)
    organisation_description = forms.CharField(label='Description', widget=forms.Textarea, required=True)
    number_of_people_served = forms.IntegerField()
    license_id = forms.CharField(label='ID')
    license_description = forms.CharField(label='Description', widget=forms.Textarea, required=True)
    validity_from = forms.DateField(label='From', widget=forms.SelectDateWidget)
    validity_to = forms.DateField(label='To', widget=forms.SelectDateWidget)
