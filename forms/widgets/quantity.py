from django import forms
from django.db.utils import ProgrammingError
from gwml2.models.general import Quantity, Unit, UnitGroup


class QuantityInput(forms.widgets.Input):
    template_name = 'widgets/quantity.html'
    input_type = 'number'
    unit_group = None
    unit_required = True

    def __init__(self, unit_group=None, unit_required=True, attrs=None):
        super().__init__(attrs)
        try:
            if unit_group:
                self.unit_group = UnitGroup.objects.get(name=unit_group)
        except (ProgrammingError, UnitGroup.DoesNotExist):
            pass
        self.unit_required = unit_required

    def get_context(self, name, value, attrs):
        context = super(QuantityInput, self).get_context(name, value, attrs)
        context['widget']['attrs']['maxlength'] = 50
        context['widget']['attrs']['placeholder'] = name.title()
        context['id'] = value
        if value:
            quantity = Quantity.objects.get(id=value)
            context['value'] = '%s' % quantity.value
            context['unit'] = quantity.unit.id if quantity.unit else ''
        else:
            context['value'] = ''
            context['unit'] = ''

        # create choices
        unit_choices = []
        units = self.unit_group.units.all() if self.unit_group else Unit.objects.all()
        for unit in units:
            unit_choices.append({
                'id': unit.id,
                'name': unit.name,
                'html': unit.html if unit.html else unit.name,
            })
        context['unit_choices'] = unit_choices
        context['unit_required'] = self.unit_required
        return context

    def value_from_datadict(self, data, files, name):
        """
        Given a dictionary of data and this widget's name, return the value
        of this widget or None if it's not provided.
        """
        try:
            if '{}_id'.format(name) in data and data['{}_id'.format(name)]:
                quantity = Quantity.objects.get(
                    id=data['{}_id'.format(name)]
                )
            else:
                quantity = Quantity()
            if data['{}_value'.format(name)]:
                quantity.value = data['{}_value'.format(name)]
                quantity.unit = None
                if data['{}_unit'.format(name)]:
                    unit, created = Unit.objects.get_or_create(name=data['{}_unit'.format(name)])
                    if created and self.unit_group:
                        self.unit_group.units.add(unit)
                    quantity.unit = unit
                quantity.save()
                return quantity.id
            else:
                if quantity.pk:
                    quantity.delete()
                return None
        except KeyError:
            return None
