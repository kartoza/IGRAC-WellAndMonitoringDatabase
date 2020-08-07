from django import forms
from django.forms.models import model_to_dict
from gwml2.models.general import Quantity
from gwml2.models.geology import GeologyLog


class GeologyLogForm(forms.ModelForm):
    """
    Form of geology log of well.
    """
    id_log = forms.CharField(required=False)
    top_depth_val = forms.CharField(required=False)
    bottom_depth_val = forms.CharField(required=False)

    class Meta:
        model = GeologyLog
        fields = ('id_log', 'top_depth_val', 'bottom_depth_val', 'material', 'geological_unit')

    @staticmethod
    def make_from_data(instance, data, files):
        """ Create form from request data
        :param instance: GeologyLog object
        :type instance: GeologyLog

        :param data: dictionary of data
        :type data: dict

        :param files: dictionary of files that uploaded
        :type files: dict

        :return: Form
        :rtype: GeologyLogForm
        """

        if data['top_depth_val']:
            top_depth, created = Quantity.objects.get_or_create(
                value=data['top_depth_val'], unit='meters')
            instance.top_depth = top_depth

        if data['bottom_depth_val']:
            bottom_depth, created = Quantity.objects.get_or_create(
                value=data['bottom_depth_val'], unit='meters')
            instance.bottom_depth = bottom_depth
        return GeologyLogForm(data, files, instance=instance)

    @staticmethod
    def make_from_instance(instance):
        """ Create form from instance
        :param instance: GeologyLog object
        :type instance: GeologyLog

        :return: Form
        :rtype: GeologyLogForm
        """
        data = model_to_dict(instance)
        data['id_log'] = instance.id
        data['top_depth_val'] = instance.top_depth.value if instance.top_depth else None
        data['bottom_depth_val'] = instance.bottom_depth.value if instance.bottom_depth else None
        return GeologyLogForm(initial=data)
