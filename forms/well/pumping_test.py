from django.forms.models import model_to_dict
from gwml2.forms.well.base import WellBaseForm
from gwml2.forms.widgets.quantity import QuantityInput
from gwml2.models.hydrogeology import PumpingTest


class PumpingTestForm(WellBaseForm):
    """
    Form for PumpingTest.
    """

    class Meta:
        model = PumpingTest
        fields = ('porosity', 'hydraulic_conductivity', 'transmissivity', 'specific_storage', 'specific_yield',
                  'storativity', 'specific_capacity', 'test_type')
        widgets = {
            'hydraulic_conductivity': QuantityInput(unit_group='length / time'),
            'transmissivity': QuantityInput(unit_group='flow rate'),
            'specific_storage': QuantityInput(unit_group='1 / length'),
            'specific_capacity': QuantityInput(unit_group='flow rate'),
            'storativity': QuantityInput(unit_group='length^3 / time'),
        }

    def __init__(self, *args, **kwargs):
        super(PumpingTestForm, self).__init__(*args, **kwargs)
        self.fields['porosity'].widget.attrs['min'] = 0
        self.fields['porosity'].widget.attrs['max'] = 100
        self.fields['hydraulic_conductivity'].widget.attrs['min'] = 0
        self.fields['transmissivity'].widget.attrs['min'] = 0
        self.fields['specific_storage'].widget.attrs['min'] = 0
        self.fields['specific_yield'].widget.attrs['min'] = 0
        self.fields['storativity'].widget.attrs['min'] = 0
        self.fields['specific_capacity'].widget.attrs['min'] = 0

        self.fields['storativity'].label = 'Yield'
        self.fields['porosity'].widget.attrs['maxlength'] = 10
        self.fields['specific_yield'].widget.attrs['maxlength'] = 10

    @staticmethod
    def make_from_data(instance, data, files):
        """ Create form from request data
        :param instance: PumpingTest object
        :type instance: PumpingTest

        :param data: dictionary of data
        :type data: dict

        :param files: dictionary of files that uploaded
        :type files: dict

        :return: Form
        :rtype: PumpingTestForm
        """
        return PumpingTestForm(data, files, instance=instance)

    @staticmethod
    def make_from_instance(instance):
        """ Create form from instance
        :param instance: PumpingTest object
        :type instance: PumpingTest

        :return: Form
        :rtype: PumpingTestForm
        """
        data = {}
        if instance:
            data = model_to_dict(instance)
        return PumpingTestForm(initial=data)
