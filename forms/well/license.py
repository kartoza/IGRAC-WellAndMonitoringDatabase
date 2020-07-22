from django import forms


class LicenseForm(forms.Form):
    """
    Form of license.
    """
    id = forms.CharField(label='ID')
    validity_from = forms.DateField()
    validity_to = forms.DateField()
    description = forms.CharField(widget=forms.Textarea, required=False)
