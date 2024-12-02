
from django import forms
from django.contrib.gis.geos import Point
from django.forms.models import model_to_dict
from django.utils.translation import ugettext_lazy as _
from gwml2.forms.well.base import WellBaseForm
from gwml2.forms.widgets.file_selection import FileSelectionInput
from gwml2.forms.widgets.quantity import QuantityInput
from gwml2.models.general import Country
from gwml2.models.well import Well


class GeneralInformationForm(WellBaseForm):
    """
    Form of general information of well.
    """
    latitude = forms.FloatField(
        help_text=_('Latitude must be expressed in decimal degrees.'), required=True)
    longitude = forms.FloatField(
        help_text=_('Longitude must be expressed in decimal degrees.'), required=True)

    class Meta:
        model = Well
        fields = (
            'ggis_uid', 'original_id', 'location', 'name', 'feature_type',
            'purpose', 'status', 'country', 'address',
            'ground_surface_elevation', 'top_borehole_elevation', 'photo',
            'description', 'glo_90m_elevation'
        )
        widgets = {
            'ground_surface_elevation': QuantityInput(unit_group='length'),
            'top_borehole_elevation': QuantityInput(unit_group='length'),
            'photo': FileSelectionInput(preview=True),
            'glo_90m_elevation': QuantityInput(unit_group='length'),
        }

    def __init__(self, *args, **kwargs):
        super(GeneralInformationForm, self).__init__(*args, **kwargs)

        self.fields['ggis_uid'].disabled = True
        self.fields['ggis_uid'].label = 'GGIS UID'
        self.fields['original_id'].label = 'Original ID'
        self.fields['name'].required = True
        self.fields['feature_type'].required = True

        self.fields['photo'].widget.attrs['accept'] = 'image/gif, image/png, image/jpeg, image/jpg'
        self.fields['description'].widget.attrs['maxlength'] = 1000
        self.fields['address'].widget.attrs['maxlength'] = 200
        self.fields['original_id'].widget.attrs['maxlength'] = 256
        self.fields['name'].widget.attrs['maxlength'] = 64

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
                x=float(data['longitude']), y=float(data['latitude']), srid=4326)
        if instance.ground_surface_elevation_id:
            data['ground_surface_elevation_id'] = instance.ground_surface_elevation_id
        if instance.top_borehole_elevation_id:
            data['top_borehole_elevation_id'] = instance.top_borehole_elevation_id
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
                data['country'] = Country.objects.get(name__iexact=data['country']).id
            except Country.DoesNotExist:
                pass
        except TypeError:
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
