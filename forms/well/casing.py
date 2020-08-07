from django import forms
from django.forms.models import model_to_dict
from gwml2.models.drilling_and_construction import Casing
from gwml2.models.general import Quantity


class CasingForm(forms.ModelForm):
    """
    Form for Casing.
    """
    id_ = forms.CharField(required=False)
    top_depth_val = forms.CharField(required=False)
    bottom_depth_val = forms.CharField(required=False)
    diameter_val = forms.CharField(required=False)

    class Meta:
        model = Casing
        fields = ('id_', 'top_depth_val', 'bottom_depth_val',
                  'diameter_val', 'material', 'description')

    @staticmethod
    def make_from_data(instance, data, files):
        """ Create form from request data
        :param instance: Casing object
        :type instance: Casing

        :param data: dictionary of data
        :type data: dict

        :param files: dictionary of files that uploaded
        :type files: dict

        :return: Form
        :rtype: CasingForm
        """
        if data['top_depth_val']:
            quantity, created = Quantity.objects.get_or_create(
                value=data['top_depth_val'], unit='meters')
            instance.top_depth = quantity
        if data['bottom_depth_val']:
            quantity, created = Quantity.objects.get_or_create(
                value=data['bottom_depth_val'], unit='meters')
            instance.bottom_depth = quantity
        if data['diameter_val']:
            quantity, created = Quantity.objects.get_or_create(
                value=data['bottom_depth_val'], unit='meters')
            instance.diameter = quantity
        return CasingForm(data, files, instance=instance)

    @staticmethod
    def make_from_instance(instance):
        """ Create form from instance
        :param instance: Casing object
        :type instance: Casing

        :return: Form
        :rtype: CasingForm
        """
        data = model_to_dict(instance)
        data['id_'] = instance.id
        data['top_depth_val'] = instance.top_depth.value if instance.top_depth else None
        data['bottom_depth_val'] = instance.bottom_depth.value if instance.bottom_depth else None
        data['diameter_val'] = instance.diameter.value if instance.diameter else None
        return CasingForm(initial=data)
