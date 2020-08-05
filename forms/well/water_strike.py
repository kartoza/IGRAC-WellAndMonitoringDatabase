from django import forms


class WaterStrikeForm(forms.Form):
    """
    Form of water strike of well.
    """
    depth = forms.FloatField(required=False)
    description = forms.CharField(required=False)
