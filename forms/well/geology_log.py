from django import forms
from gwml2.models.well import GWWell


class GeologyLogForm(forms.Form):
    """
    Form of geology log of well.
    """
    # identification
    id = forms.ModelMultipleChoiceField(
        queryset=GWWell.objects.all())
    start_depth = forms.FloatField(
        label='From', required=False)
    end_depth = forms.FloatField(
        label='To', required=False)
    phenomenon_time = forms.DateTimeField(
        label='Phenomenon time', required=False)
    result_time = forms.DateTimeField(
        label='Result time', required=False)
    result = forms.CharField(
        label='Result', required=False)
