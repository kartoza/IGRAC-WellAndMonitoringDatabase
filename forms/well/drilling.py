from datetime import datetime
from django.forms.models import model_to_dict
from gwml2.forms.well.base import WellBaseForm
from gwml2.models.drilling import Drilling


class DrillingForm(WellBaseForm):
    """
    Form for Drilling.
    """

    class Meta:
        model = Drilling
        fields = ('drilling_method', 'driller', 'successful', 'cause_of_failure', 'year_of_drilling')

    def __init__(self, *args, **kwargs):
        super(DrillingForm, self).__init__(*args, **kwargs)
        self.fields['year_of_drilling'].widget.attrs['min'] = 1900
        self.fields['year_of_drilling'].widget.attrs['maxlength'] = 4
        self.fields['year_of_drilling'].widget.attrs['max'] = datetime.now().year

    @staticmethod
    def make_from_data(instance, data, files):
        """ Create form from request data
        :param instance: Drilling object
        :type instance: Drilling

        :param data: dictionary of data
        :type data: dict

        :param files: dictionary of files that uploaded
        :type files: dict

        :return: Form
        :rtype: DrillingForm
        """
        # if parameter is string
        try:
            if data['successful'].lower() == 'yes':
                data['successful'] = True
            elif data['successful'].lower() == 'no':
                data['successful'] = False
        except KeyError:
            data['successful'] = instance.successful
        return DrillingForm(data, files, instance=instance)

    @staticmethod
    def make_from_instance(instance):
        """ Create form from instance
        :param instance: Drilling object
        :type instance: Drilling

        :return: Form
        :rtype: DrillingForm
        """
        data = {}
        if instance:
            data = model_to_dict(instance)
        return DrillingForm(initial=data, instance=instance)
