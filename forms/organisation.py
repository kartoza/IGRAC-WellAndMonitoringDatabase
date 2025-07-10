from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth import get_user_model
from django.urls import reverse

from geonode.base.models import License, RestrictionCodeType
from gwml2.forms.widgets.multi_value import MultiValueInput
from gwml2.models.well_management.organisation import Organisation

User = get_user_model()


class OrganisationFormAdmin(forms.ModelForm):
    """Organisation form for admin.

    This is needed for user and editor selector.
    """
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
    license = forms.ModelChoiceField(
        License.objects.all(), required=False
    )
    restriction_code_type = forms.ModelChoiceField(
        RestrictionCodeType.objects.all(), required=False
    )

    class Meta:
        model = Organisation
        fields = (
            'name', 'country', 'description',
            'data_is_from_api', 'data_date_start', 'data_date_end',
            'data_is_groundwater_level', 'data_is_groundwater_quality',
            'admin_users', 'editor_users',
            'license', 'restriction_code_type', 'constraints_other'
        )

    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        if self.instance:
            self.fields['admin_users'].initial = User.objects.filter(
                id__in=self.instance.admins)
            self.fields['editor_users'].initial = User.objects.filter(
                id__in=self.instance.editors)

    def save(self, commit=True):
        """Save admin and editor users."""
        instance = super(OrganisationFormAdmin, self).save(commit)
        admin_users = self.cleaned_data.get('admin_users', None)
        if admin_users is not None:
            admin_users = admin_users.values_list('id', flat=True)
            instance.admins = list(admin_users)
        editor_users = self.cleaned_data.get('editor_users', None)
        if editor_users is not None:
            editor_users = editor_users.values_list('id', flat=True)
            instance.editors = list(editor_users)
        instance.save()
        return instance


class OrganisationForm(OrganisationFormAdmin):
    """Organisation form for frontend.

    Having autocomplete widget for user.
    """

    def __init__(self, *args, **kwargs):
        super(OrganisationForm, self).__init__(*args, **kwargs)
        # init widget
        self.fields['admin_users'].widget = MultiValueInput(
            url=reverse('user_autocomplete'), Model=User
        )
        self.fields['editor_users'].widget = MultiValueInput(
            url=reverse('user_autocomplete'), Model=User
        )
