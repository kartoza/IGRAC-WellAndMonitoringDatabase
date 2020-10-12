from django import forms


class CsvWellForm(forms.Form):
    """
    Form to upload CSV file.
    """

    gw_well_file = forms.FileField(
        label="Well Descriptors:",
        widget=forms.FileInput(),
        required=False
    )
