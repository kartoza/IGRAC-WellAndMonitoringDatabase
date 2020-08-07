from django import forms
from django.forms.models import model_to_dict
from gwml2.models.general import Quantity
from gwml2.models.geology import Geology


class GeologyForm(forms.ModelForm):
    """
    Form of geology of well.
    """
    depth = forms.CharField(required=False, label='Total depth')

    class Meta:
        model = Geology
        fields = ('depth', 'total_depth')

    @staticmethod
    def make_from_data(instance, data, files):
        """ Create form from request data
        :param instance: Geology object
        :type instance: Geology

        :param data: dictionary of data
        :type data: dict

        :param files: dictionary of files that uploaded
        :type files: dict

        :return: Form
        :rtype: GeologyForm
        """
        if data['total_depth']:
            total_depth, created = Quantity.objects.get_or_create(
                value=data['total_depth'], unit='meters')
            data['total_depth'] = total_depth.id
        return GeologyForm(data, files, instance=instance)

    @staticmethod
    def make_from_instance(instance):
        """ Create form from instance
        :param instance: Geology object
        :type instance: Geology

        :return: Form
        :rtype: GeologyForm
        """
        data = {}
        if instance:
            data = model_to_dict(instance)
            data['depth'] = instance.total_depth.value if instance.total_depth else None
        return GeologyForm(initial=data)
