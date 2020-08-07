from django import forms
from gwml2.models.general import Quantity


class QuantityInput(forms.widgets.Input):
    template_name = 'widgets/quantity.html'
    input_type = 'text'

    def __init__(self, unit_choices=list, attrs=None):
        super().__init__(attrs)
        self.unit_choices = unit_choices

    def get_context(self, name, value, attrs):
        context = super(QuantityInput, self).get_context(name, value, attrs)
        context['widget']['attrs']['maxlength'] = 50
        context['widget']['attrs']['placeholder'] = name.title()
        if value:
            quantity = Quantity.objects.get(id=value)
            context['value'] = '%s' % quantity.value
            context['unit'] = quantity.unit
        else:
            context['value'] = ''
            context['unit'] = ''
        context['unit_choices'] = self.unit_choices
        return context

    def value_from_datadict(self, data, files, name):
        """
        Given a dictionary of data and this widget's name, return the value
        of this widget or None if it's not provided.
        """
        try:
            if data['{}_value'.format(name)]:
                quantity, created = Quantity.objects.get_or_create(
                    value=data['{}_value'.format(name)],
                    unit=data['{}_unit'.format(name)]
                )
                return quantity.id
            else:
                return None
        except KeyError:
            return None
