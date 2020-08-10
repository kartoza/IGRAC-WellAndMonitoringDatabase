from django import forms
from django.contrib.gis.geos import Point
from django.forms.models import model_to_dict
from gwml2.forms.widgets import QuantityInput
from gwml2.models.well import Well


class GeneralInformationForm(forms.ModelForm):
    """
    Form of general information of well.
    """
    id = forms.CharField(
        label='GGIS ID', disabled=True, required=False)
    latitude = forms.FloatField(
        help_text='latitude of well', min_value=-90, max_value=90)
    longitude = forms.FloatField(
        help_text='longitude of well', min_value=-180, max_value=180)

    class Meta:
        model = Well
        fields = ('original_id', 'location', 'name', 'feature_type', 'country', 'address', 'elevation', 'photo', 'description')
        widgets = {
            'elevation': QuantityInput(unit_group='elevation'),
        }

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
        if data['photo']:
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
        data['latitude'] = instance.location.y
        data['longitude'] = instance.location.x
        return GeneralInformationForm(initial=data)
