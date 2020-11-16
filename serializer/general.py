class WellSerializer(object):
    """ Specifically serialize special field"""

    def quantity(self, field_name, obj):
        """ Return quantity divide by the id, unit name and value as key

        :param field_name: field name of the object
        :type field_name: str

        :param obj:
        :type obj: Quantity
        """
        data = {}
        data['{}_id'.format(field_name)] = ''
        data['{}_unit'.format(field_name)] = ''
        data['{}_value'.format(field_name)] = ''
        if obj:
            data['{}_id'.format(field_name)] = obj.id
            data['{}_value'.format(field_name)] = obj.value
            if obj.unit:
                data['{}_unit'.format(field_name)] = obj.unit.name

        return data

    def reference_elevation(self, field_name, obj):
        """ Return reference elevation divide by the id, unit name, value and reference as key

        :param field_name: field name of the object
        :type field_name: str

        :param obj:
        :type obj: ReferenceElevation
        """
        data = {}
        data['{}_id'.format(field_name)] = ''
        data['{}_unit'.format(field_name)] = ''
        data['{}_value'.format(field_name)] = ''
        data['{}_reference'.format(field_name)] = ''
        if obj:
            data['{}_id'.format(field_name)] = obj.id
            data['{}_reference'.format(field_name)] = obj.reference.id
            if obj.value:
                data['{}_value'.format(field_name)] = obj.value.value
                if obj.value.unit:
                    data['{}_unit'.format(field_name)] = obj.value.unit.name

        return data
