from django import forms


class BaseMultiValueInput(forms.widgets.FileInput):
    template_name = 'widgets/multi_value.html'

    def __init__(self, url='', attrs=None):
        super().__init__(attrs)
        self.url = url

    def get_context(self, name, value, attrs):
        context = super(BaseMultiValueInput, self).get_context(name, value, attrs)
        context['url'] = self.url
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
        except (KeyError, ValueError):
            return []

    def selected(self, value):
        """ return list dictionary of selected onw
        :return: dictionary of selected [{id,label}]
        :rtype: dict
        """
        raise NotImplementedError
