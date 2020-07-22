from django import forms


class MeasurementForm(forms.Form):
    """
    Form of measurement
    """
    time = forms.DateTimeField(label="Date and Time", required=False)
    parameter = forms.CharField(required=False)
    facility = forms.CharField(required=False)
    value = forms.CharField(required=False)
    unit = forms.CharField(required=False)
