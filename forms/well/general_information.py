import copy
from django import forms
from django.contrib.gis.geos import Point
from django.forms.models import model_to_dict
from gwml2.models.general import Quantity
from gwml2.models.well import Well


class GeneralInformationForm(forms.ModelForm):
    """
    Form of general information of well.
    """
    latitude = forms.FloatField(
        help_text='latitude of well', min_value=-90, max_value=90)
    longitude = forms.FloatField(
        help_text='longitude of well', min_value=-180, max_value=180)
    elevation_val = forms.CharField(help_text='elevation of well', label='elevation')

    class Meta:
        model = Well
        fields = ('id_well', 'location', 'name', 'feature_type', 'country', 'address', 'elevation', 'photo', 'description')

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
        data = copy.deepcopy(data)
        data['location'] = Point(
            x=float(data['longitude']), y=float(data['latitude']), srid=4326)
        if data['elevation_val']:
            elevation, created = Quantity.objects.get_or_create(value=data['elevation_val'], unit='a.s.l.')
            data['elevation'] = elevation.id

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
        data['elevation_val'] = instance.elevation.value if instance.elevation else ''
        data['latitude'] = instance.location.y
        data['longitude'] = instance.location.x
        data['id'] = instance.id_well
        return GeneralInformationForm(initial=data)
