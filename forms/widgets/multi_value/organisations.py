from gwml2.forms.widgets.multi_value.base import BaseMultiValueInput
from gwml2.models.well_management.organisation import Organisation


class MultiOrganisationInput(BaseMultiValueInput):
    def selected(self, value):
        """ return list dictionary of selected onw
        :return: dictionary of selected [{id,label}]
        :rtype: dict
        """
        return [
            {'id': org.id, 'label': org.name} for org in Organisation.objects.filter(id__in=value)
        ]
