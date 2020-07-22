from django import forms


class GeologyForm(forms.Form):
    """
    Form of geology of well.
    """
    total_depth = forms.FloatField()
