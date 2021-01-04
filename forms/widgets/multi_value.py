from django import forms


class MultiValueInput(forms.widgets.FileInput):
    template_name = 'widgets/multi_value.html'
    Model = None

    def __init__(self, url='', Model=None, attrs=None):
        super().__init__(attrs)
        self.url = url
        self.Model = Model

    def get_context(self, name, value, attrs):
        context = super(MultiValueInput, self).get_context(name, value, attrs)
        context['url'] = self.url
        if value is None:
            value = []
        context['value'] = ','.join(['{}'.format(val) for val in value])
        context['selected'] = self.selected(value)
        return context

    def value_from_datadict(self, data, files, name):
        """
        Given a dictionary of data and this widget's name, return the value
        of this widget or None if it's not provided.
        """
        try:
            ids = [int(row) for row in data['{}'.format(name)].split(',')]
            return ids
        except (KeyError, ValueError) as e:
            return []

    def selected(self, value):
        """ return list dictionary of selected onw
        :return: dictionary of selected [{id,label}]
        :rtype: dict
        """
        return [
            {
                'id': model.id,
                'label': model.__str__()
            } for model in self.Model.objects.filter(id__in=value)
        ]
