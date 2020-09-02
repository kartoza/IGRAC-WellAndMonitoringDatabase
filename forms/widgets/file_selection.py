import os
from django import forms


class FileSelectionInput(forms.widgets.FileInput):
    template_name = 'widgets/file_selection.html'
    read_only = False

    def __init__(self, read_only=False, attrs=None):
        super().__init__(attrs)
        self.read_only = read_only

    def get_context(self, name, value, attrs):
        context = super(FileSelectionInput, self).get_context(name, value, attrs)
        if value:
            context['value'] = os.path.basename(value.name)
        context['read_only'] = self.read_only
        return context
