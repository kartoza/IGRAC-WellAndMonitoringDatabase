from gwml2.models.general import Quantity, Unit
from gwml2.models.reference_elevation import ReferenceElevation
from gwml2.models.term import TermReferenceElevationType
from gwml2.forms.widgets.quantity import QuantityInput


class ReferenceElevationInput(QuantityInput):
    template_name = 'widgets/reference_elevation.html'

    def __init__(self, unit_group=None, unit_required=True, attrs=None):
        super(ReferenceElevationInput, self).__init__(unit_group, unit_required, attrs)

    def get_context(self, name, value, attrs):
        quantity = None
        if value:
            reference = ReferenceElevation.objects.get(id=value)
            quantity = reference.value.id
        else:
            reference = None

        context = super(ReferenceElevationInput, self).get_context(name, quantity, attrs)
        context['id'] = value
        if reference:
            context['reference'] = reference.reference.id
        else:
            context['reference'] = ''

        # create choices
        reference_choices = []
        for reference in TermReferenceElevationType.objects.all():
            reference_choices.append({
                'id': reference.id,
                'name': reference.name
            })
        context['reference_choices'] = reference_choices
        return context

    def value_from_datadict(self, data, files, name):
        """
        Given a dictionary of data and this widget's name, return the value
        of this widget or None if it's not provided.
        """
        try:
            if data['{}_id'.format(name)]:
                elevation = ReferenceElevation.objects.get(
                    id=data['{}_id'.format(name)]
                )
            else:
                elevation = ReferenceElevation(
                    value=Quantity(value=0))

            if data['{}_value'.format(name)]:
                quantity = elevation.value
                quantity.value = data['{}_value'.format(name)]
                unit, created = Unit.objects.get_or_create(name=data['{}_unit'.format(name)])
                if created and self.unit_group:
                    self.unit_group.units.add(unit)
                quantity.unit = unit
                quantity.save()

                # reference
                if data['{}_reference'.format(name)]:
                    elevation.reference = TermReferenceElevationType.objects.get(
                        id=data['{}_reference'.format(name)]
                    )
                elevation.value = quantity
                elevation.save()
                return elevation.id
            else:
                if elevation.pk and elevation.value.pk:
                    elevation.value.delete()
                return None
        except KeyError:
            return None
