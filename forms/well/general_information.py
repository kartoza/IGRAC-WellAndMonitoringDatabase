from django import forms
from django.contrib.gis.geos import Point
from django.forms.models import model_to_dict
from django.utils.translation import gettext_lazy as _

from gwml2.forms.well.base import WellBaseForm
from gwml2.forms.widgets.file_selection import FileSelectionInput
from gwml2.forms.widgets.quantity import QuantityInput
from gwml2.models.general import Country
from gwml2.models.term import TermFeatureType
from gwml2.models.well import Well
from gwml2.models.well_quality_control import WellQualityControl


class GeneralInformationForm(WellBaseForm):
    """
    Form of general information of well.
    """
    latitude = forms.FloatField(
        help_text=_('Latitude must be expressed in decimal degrees.'),
        required=True)
    longitude = forms.FloatField(
        help_text=_('Longitude must be expressed in decimal degrees.'),
        required=True)

    # Data Quality
    data_quality = forms.CharField(
        required=False,
        disabled=True
    )

    class Meta:
        model = Well
        fields = (
            'ggis_uid', 'original_id', 'location', 'name', 'feature_type',
            'purpose', 'status', 'country', 'address',
            'ground_surface_elevation', 'top_borehole_elevation', 'photo',
            'description', 'glo_90m_elevation',
            'is_groundwater_level', 'is_groundwater_quality',
            'estimated_flow'
        )
        widgets = {
            'ground_surface_elevation': QuantityInput(unit_group='length'),
            'top_borehole_elevation': QuantityInput(unit_group='length'),
            'photo': FileSelectionInput(preview=True),
            'glo_90m_elevation': QuantityInput(unit_group='length'),
        }

    def __init__(self, *args, **kwargs):
        from gwml2.models.site_preference import SitePreference
        preferences = SitePreference.load()
        super(GeneralInformationForm, self).__init__(*args, **kwargs)

        self.fields['ggis_uid'].disabled = True
        self.fields['ggis_uid'].label = 'GGIS UID'
        self.fields['original_id'].label = 'Original ID'
        self.fields['name'].required = True
        self.fields['feature_type'].required = True
        self.fields['feature_type'].queryset = self.fields[
            'feature_type'
        ].queryset.order_by('-name')

        self.fields['photo'].widget.attrs[
            'accept'] = 'image/gif, image/png, image/jpeg, image/jpg'
        self.fields['description'].widget.attrs['maxlength'] = 1000
        self.fields['address'].widget.attrs['maxlength'] = 200
        self.fields['original_id'].widget.attrs['maxlength'] = 256
        self.fields['name'].widget.attrs['maxlength'] = 512

        instance = None
        if self.instance.id:
            instance = self.instance
        try:
            if kwargs.get('initial', None):
                if kwargs.get('initial').get('id', None):
                    instance = Well.objects.get(
                        id=kwargs.get('initial').get('id')
                    )
        except Exception:
            pass

        if instance:
            try:
                flags = []
                # This is for data quality
                quality_control = WellQualityControl.objects.get(well=instance)
                if quality_control.groundwater_level_time_gap:
                    flags.append(
                        f'There is a data gap of more than '
                        f'{preferences.groundwater_level_quality_control_days_gap / 365} '
                        f'years'
                    )
                if quality_control.groundwater_level_value_gap:
                    flags.append(
                        f'There is a jump of '
                        f'+{preferences.groundwater_level_quality_control_level_gap}m '
                        f'or '
                        f'-{preferences.groundwater_level_quality_control_level_gap}m '
                    )
                if quality_control.groundwater_level_strange_value:
                    flags.append(
                        f'There is a strange value.'
                    )
                if flags:
                    self.fields['data_quality'].initial = 'Needs review'
                    self.fields['data_quality'].help_text = ',  '.join(flags)
                else:
                    self.fields['data_quality'].initial = 'No flags'
            except WellQualityControl.DoesNotExist:
                self.fields['data_quality'].initial = '-'

    @staticmethod
    def make_from_data(instance, data, files):
        """ Create form from request data
        :param instance: well object
        :type instance: Well

        :param data: dictionary of data
        :type data: dict

        :param files: dictionary of files that uploaded
        :type files: dict

        :return: Form
        :rtype: GeneralInformationForm
        """
        if data['longitude'] and data['latitude']:
            data['location'] = Point(
                x=float(data['longitude']), y=float(data['latitude']),
                srid=4326
            )
        if instance.ground_surface_elevation_id:
            data[
                'ground_surface_elevation_id'] = instance.ground_surface_elevation_id
        if instance.top_borehole_elevation_id:
            data[
                'top_borehole_elevation_id'] = instance.top_borehole_elevation_id
        if instance.glo_90m_elevation_id:
            data['glo_90m_elevation_id'] = instance.glo_90m_elevation_id

        # check the files
        form_files = {}
        photo = data.get('photo', None)
        if not photo:
            instance.photo = None
        elif photo and files.get(photo, None):
            form_files = {
                'photo': files.get(photo, None)
            }

        # if country is string
        try:
            int(data['country'])
        except ValueError:
            try:
                data['country'] = Country.objects.get(
                    name__iexact=data['country']
                ).id
            except Country.DoesNotExist:
                pass
        except TypeError:
            pass

        # if feature_type is not spring
        # estimated_flow is null
        try:
            feature_type = TermFeatureType.objects.get(id=data['feature_type'])
            if feature_type.name.lower() != 'spring':
                data['estimated_flow'] = None
        except TermFeatureType.DoesNotExist:
            pass

        return GeneralInformationForm(data, form_files, instance=instance)

    @staticmethod
    def make_from_instance(instance):
        """ Create form from instance
        :param instance: well object
        :type instance: Well

        :return: Form
        :rtype: GeneralInformationForm
        """
        data = model_to_dict(instance)
        data['id'] = instance.id
        if instance.location:
            data['latitude'] = round(instance.location.y, 7)
            data['longitude'] = round(instance.location.x, 7)
        else:
            data['latitude'] = None
            data['longitude'] = None
        return GeneralInformationForm(
            initial=data
        )
