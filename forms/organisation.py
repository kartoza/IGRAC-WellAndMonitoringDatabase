from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth import get_user_model
from django.urls import reverse
from geonode.groups.models import GroupProfile

from gwml2.forms.widgets.multi_value import MultiValueInput
from gwml2.models.well_management.organisation import Organisation

User = get_user_model()


class OrganisationFormAdmin(forms.ModelForm):
    admin_users = forms.ModelMultipleChoiceField(
        User.objects.all(),
        widget=FilteredSelectMultiple('admin_users', False),
        required=False
    )
    editor_users = forms.ModelMultipleChoiceField(
        User.objects.all(),
        widget=FilteredSelectMultiple('editor_users', False),
        required=False
    )
    selected_groups = forms.ModelMultipleChoiceField(
        GroupProfile.objects.all(),
        widget=FilteredSelectMultiple('selected_groups', False),
        label='Groups',
        required=False
    )

    class Meta:
        model = Organisation
        fields = (
            'name', 'description', 'admin_users', 'editor_users',
            'selected_groups'
        )

    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        if self.instance:
            self.fields['admin_users'].initial = User.objects.filter(
                id__in=self.instance.admins)
            self.fields['editor_users'].initial = User.objects.filter(
                id__in=self.instance.editors)
            self.fields[
                'selected_groups'].initial = GroupProfile.objects.filter(
                id__in=self.instance.groups)

    def clean_admin_users(self):
        users = self.cleaned_data.get('admin_users', None)
        if users is not None:
            return list(users.values_list('id', flat=True))
        else:
            return []

    def clean_editor_users(self):
        users = self.cleaned_data.get('editor_users', None)
        if users is not None:
            return list(users.values_list('id', flat=True))
        else:
            return []

    def clean_selected_groups(self):
        selected_groups = self.cleaned_data.get('selected_groups', None)
        if selected_groups is not None:
            return list(selected_groups.values_list('id', flat=True))
        else:
            return []

    def save(self, commit=True):
        instance = super(OrganisationFormAdmin, self).save(commit)
        instance.admins = self.cleaned_data.get('admin_users', [])
        instance.editors = self.cleaned_data.get('editor_users', [])
        instance.groups = self.cleaned_data.get('selected_groups', [])
        instance.save()
        return instance


class OrganisationForm(OrganisationFormAdmin):
    def __init__(self, *args, **kwargs):
        super(OrganisationForm, self).__init__(*args, **kwargs)
        # init widget
        self.fields['admin_users'].widget = MultiValueInput(
            url=reverse('user_autocomplete'), Model=User
        )
        self.fields['editor_users'].widget = MultiValueInput(
            url=reverse('user_autocomplete'), Model=User
        )
        self.fields['selected_groups'].widget = MultiValueInput(
            url=reverse('group_autocomplete'), Model=GroupProfile
        )
