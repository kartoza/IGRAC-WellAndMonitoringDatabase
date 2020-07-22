from django import forms

DOCUMENT_TYPE = (
    ('picture', 'picture'),
    ('other', 'other')
)


class DocumentForm(forms.Form):
    """
    Form of document of well.
    """
    file = forms.FileField(required=False)
    document_type = forms.ChoiceField(
        choices=DOCUMENT_TYPE,
        widget=forms.Select())
    description = forms.CharField(required=False)
    file_type = forms.CharField(required=False, disabled=True)
    file_size = forms.CharField(required=False, disabled=True)
