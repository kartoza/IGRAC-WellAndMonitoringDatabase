from django import forms
from django.contrib import admin
from gwml2.models.well_management.organisation import Organisation
from django.contrib.auth import get_user_model
from django.contrib.admin.widgets import FilteredSelectMultiple

User = get_user_model()


class OrganisationForm(forms.ModelForm):
    viewer_users = forms.ModelMultipleChoiceField(
        User.objects.all(),
        widget=FilteredSelectMultiple('viewer_users', False),
        required=False
    )
    editor_users = forms.ModelMultipleChoiceField(
        User.objects.all(),
        widget=FilteredSelectMultiple('editor_users', False),
        required=False
    )

    class Meta:
        model = Organisation
        fields = ('name', 'description', 'viewer_users', 'editor_users')

    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        if self.instance:
            self.fields['viewer_users'].initial = User.objects.filter(
                id__in=self.instance.viewers)
            self.fields['editor_users'].initial = User.objects.filter(
                id__in=self.instance.editors)

    def save(self, commit=True):
        instance = super(OrganisationForm, self).save(commit)
        viewer_users = self.cleaned_data.get('viewer_users', None)
        if viewer_users is not None:
            viewer_users = viewer_users.values_list('id', flat=True)
            instance.viewers = list(viewer_users)
        editor_users = self.cleaned_data.get('editor_users', None)
        if editor_users is not None:
            editor_users = editor_users.values_list('id', flat=True)
            instance.editors = list(editor_users)
        return instance


class OrganisationAdmin(admin.ModelAdmin):
    form = OrganisationForm


admin.site.register(Organisation, OrganisationAdmin)
