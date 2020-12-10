from django import forms
from django.contrib.gis.geos import Point
from django.forms.models import model_to_dict
from gwml2.forms.well.base import WellBaseForm
from gwml2.forms.widgets.file_selection import FileSelectionInput
from gwml2.forms.widgets.quantity import QuantityInput
from gwml2.models.well import Well


class GeneralInformationForm(WellBaseForm):
    """
    Form of general information of well.
    """
    latitude = forms.FloatField(
        help_text='Latitude must be expressed in decimal degrees.', min_value=-90, max_value=90)
    longitude = forms.FloatField(
        help_text='Longitude must be expressed in decimal degrees.', min_value=-180, max_value=180)

    class Meta:
        model = Well
        fields = ('ggis_uid', 'original_id', 'location', 'name', 'feature_type', 'purpose', 'status', 'country', 'address', 'ground_surface_elevation', 'top_borehole_elevation', 'photo', 'description')
        widgets = {
            'ground_surface_elevation': QuantityInput(unit_group='length'),
            'top_borehole_elevation': QuantityInput(unit_group='length'),
            'photo': FileSelectionInput(preview=True),
        }

    def __init__(self, *args, **kwargs):
        super(GeneralInformationForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['ggis_uid'].disabled = True
        self.fields['ggis_uid'].label = 'GGIS UID'
        self.fields['feature_type'].required = True

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
        data['location'] = Point(
            x=float(data['longitude']), y=float(data['latitude']), srid=4326)

        # check the files
        if data.get('photo', None):
            files = {
                'photo': files[data['photo']]
            }
        else:
            files = {}

        return GeneralInformationForm(data, files, instance=instance)

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
