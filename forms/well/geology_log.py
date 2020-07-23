from django import forms


class GeologyLogForm(forms.Form):
    """
    Form of geology log of well.
    """
    # identification
    start_depth = forms.FloatField(required=False)
    end_depth = forms.FloatField(required=False)
    phenomenon_time = forms.DateTimeField(required=False)
    result_time = forms.DateTimeField(required=False)
    result = forms.CharField(required=False)
