from django import forms


class GeneralInformationForm(forms.Form):
    """
    Form of general information of well.
    """
    # identification
    id = forms.CharField()
    water_point_reference = forms.CharField()
    water_point_type = forms.CharField()

    # Location Information
    latitude = forms.FloatField()
    longitude = forms.FloatField()
    country = forms.CharField()
    address = forms.CharField(widget=forms.Textarea, required=False)
    elevation = forms.CharField()

    # Summary Information
    picture = forms.FileField(required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)
