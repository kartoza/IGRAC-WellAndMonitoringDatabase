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

    def get_val(self, value):
        if value is None:
            return ''
        else:
            if value is False:
                return 'No'
            elif value is True:
                return 'Yes'
        return value if value else ''

    def term_val(self, value):
        """ return value of term """
        return value.name if value else ''

    def get_quantity(self, value):
        """ return value of quantity """
        return value.__str__() if value else ''

    def get_length_to_meter(self, value):
        """ return value of quantity of lenght to meter
        :type value: Quantity
        """
        if not value:
            return ''
        else:
            return value.convert('m')
