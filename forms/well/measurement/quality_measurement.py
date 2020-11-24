from django import forms
from django.forms.models import model_to_dict
from gwml2.forms.widgets.quantity import QuantityInput
from gwml2.forms.well.base import WellBaseForm
from gwml2.models.term_measurement_parameter import TermMeasurementParameterGroup
from gwml2.models.well import WellQualityMeasurement


class WellQualityMeasurementForm(WellBaseForm):
    """
    Form of WellQualityMeasurement of well.
    """
    id = forms.CharField(required=False)

    class Meta:
        model = WellQualityMeasurement
        fields = ('id', 'time', 'parameter', 'methodology', 'value')
        widgets = {
            'value': QuantityInput(unit_required=False)
        }

    field_order = ('id', 'time', 'parameter', 'methodology', 'value')

    def __init__(self, *args, **kwargs):
        super(WellQualityMeasurementForm, self).__init__(*args, **kwargs)
        try:
            self.fields['parameter'].queryset = TermMeasurementParameterGroup.objects.get(
                name='Quality Measurement').parameters.all()
        except TermMeasurementParameterGroup.DoesNotExist:
            pass

    @staticmethod
    def make_from_data(instance, data, files):
        """ Create form from request data
        :param instance: WellWellQualityMeasurement object
        :type instance: WellWellQualityMeasurement

        :param data: dictionary of data
        :type data: dict

        :param files: dictionary of files that uploaded
        :type files: dict

        :return: Form
        :rtype: WellWellQualityMeasurementForm
        """

        return WellQualityMeasurementForm(data, files, instance=instance)

    @staticmethod
    def make_from_instance(instance):
        """ Create form from instance
        :param instance: WellWellQualityMeasurement object
        :type instance: WellWellQualityMeasurement

        :return: Form
        :rtype: WellWellQualityMeasurementForm
        """
        data = model_to_dict(instance)
        data['id'] = instance.id
        return WellQualityMeasurementForm(initial=data, instance=instance)
