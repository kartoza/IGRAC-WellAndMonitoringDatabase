"""Forms for handling well data download requests."""

from typing import Any

from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from gwml2.models.download_request import DownloadRequest
from gwml2.models.general import Country
from gwml2.models.well_management.organisation import Organisation, OrganisationType

User = get_user_model()


class TaggableMultipleChoiceField(forms.MultipleChoiceField):
    """MultipleChoiceField that accepts values outside of `choices`."""

    def valid_value(self, value):
        return True


class DownloadRequestBaseForm(forms.ModelForm):
    """Abstract base form for download requests."""

    OTHERS_VALUE = "__others__"

    organization_types = TaggableMultipleChoiceField(required=True)

    class Meta:
        model = DownloadRequest
        fields = ()

    def default_init(self):
        """Default initialization of the form."""
        self.fields["profession"].required = True
        self.fields["country"].required = True
        self.fields["email"].required = True

        known_types = [_type.name for _type in OrganisationType.objects.all()]
        self.fields["organization_types"].choices = [(name, name) for name in known_types] + [
            (self.OTHERS_VALUE, _("Others (specify)"))
        ]
        self.fields["organization_types"].label = _("Type of organization")

        # Handle other value
        self.initial_other_value = ""
        initial_types = self.initial.get("organization_types")
        if not initial_types:
            initial_types_from_post = self.data.getlist("organization_types")
            if initial_types_from_post:
                initial_types = [t.strip() for t in initial_types_from_post if t.strip()]

        if initial_types:
            if isinstance(initial_types, str):
                initial_types = [t.strip() for t in initial_types.split(",") if t.strip()]
            other_values = [t for t in initial_types if t not in known_types]
            if other_values:
                self.initial["organization_types"] = [
                    t for t in initial_types if t in known_types
                ] + [self.OTHERS_VALUE]
                self.initial_other_value = ", ".join(other_values)

    def clean_organization_types(self):
        types = [
            _type for _type in self.cleaned_data["organization_types"] if _type != self.OTHERS_VALUE
        ]
        return ", ".join(types)


class DownloadRequestForm(DownloadRequestBaseForm):
    radio_filter_type = forms.ChoiceField(
        label="Filter by",
        choices=[("data_providers", "Data Providers"), ("countries", "Countries")],
        widget=forms.RadioSelect,
        initial="data_providers",
    )

    class Meta:
        model = DownloadRequest
        fields = (
            "countries",
            "organisations",
            "email",
            "profession",
            "organization_types",
            "country",
            "data_type",
        )

    def __init__(self, *args, **kwargs):
        super(DownloadRequestForm, self).__init__(*args, **kwargs)

        self.fields["countries"].label = "Select the countries whose data you want to download."
        self.fields[
            "organisations"
        ].label = "Select the data providers whose data you want to download."
        self.default_init()

    def clean_countries(self):
        countries = self.cleaned_data["countries"]
        if "all" in countries:
            return Country.objects.all()
        else:
            return Country.objects.filter(id__in=countries)

    def clean_organisations(self):
        organisations = self.cleaned_data["organisations"]
        if "all" in organisations:
            return Organisation.objects.filter(active=True)
        else:
            return Organisation.objects.filter(id__in=organisations).filter(active=True)

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        field_name = cleaned_data.get("radio_filter_type", "countries")
        if field_name == "countries" and not cleaned_data.get("countries"):
            raise forms.ValidationError(
                {"countries": ("Please select at least one of the countries")}
            )
        if field_name == "data_providers" and not cleaned_data.get("organisations"):
            raise forms.ValidationError(
                {"organisations": ("Please select at least one of the organisations")}
            )
        return cleaned_data


def validate_wells_id(wells_id: list) -> list[int]:
    """Parse and validate a list of well IDs. Returns a clean list of ints.

    Raises ValueError with a human-readable message on failure.
    """
    try:
        ids = [int(i) for i in wells_id if i]
    except (ValueError, TypeError):
        raise ValueError("wells_id must be a list of integers.")
    if len(ids) < 1:
        raise ValueError("At least 1 well must be selected.")
    if len(ids) > 10000:
        raise ValueError("Cannot request more than 10,000 wells at once.")
    return ids


class DownloadRequestByIdsForm(DownloadRequestBaseForm):
    """Download request form for downloading data by ids."""

    wells_id = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        model = DownloadRequest
        fields = ("wells_id", "email", "profession", "organization_types", "country", "data_type")

    def __init__(self, *args, **kwargs):
        super(DownloadRequestByIdsForm, self).__init__(*args, **kwargs)
        self.default_init()

    def clean_wells_id(self):
        try:
            return validate_wells_id(self.data.getlist("wells_id"))
        except ValueError as e:
            raise forms.ValidationError(str(e))
