import os
from django import forms
from django.forms.models import model_to_dict
from gwml2.models.well import WellDocument
from gwml2.utilities import convert_size


class DocumentForm(forms.ModelForm):
    """
    Form of document of well.
    """
    id_doc = forms.CharField(required=False)
    file_type = forms.CharField(required=False, disabled=True)
    file_size = forms.CharField(required=False, disabled=True)
    time = forms.CharField(required=False, disabled=True, label='uploaded at')

    class Meta:
        model = WellDocument
        fields = ('id_doc', 'file', 'description', 'time', 'file_type', 'file_size')

    @staticmethod
    def make_from_data(instance, data, files):
        """ Create form from request data
        :param instance: WellDocument object
        :type instance: WellDocument

        :param data: dictionary of data
        :type data: dict

        :param files: dictionary of files that uploaded
        :type files: dict

        :return: Form
        :rtype: DocumentForm
        """
        # check the files
        if data['file']:
            files = {
                'file': files[data['file']]
            }
        else:
            files = {}

        return DocumentForm(data, files, instance=instance)

    @staticmethod
    def make_from_instance(instance):
        """ Create form from instance
        :param instance: WellDocument object
        :type instance: WellDocument

        :return: Form
        :rtype: DocumentForm
        """
        data = model_to_dict(instance)
        data['id_doc'] = instance.id
        data['time'] = instance.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
        filename, file_extension = os.path.splitext(instance.file.url)
        data['file_type'] = file_extension.replace('.', '')
        data['file_size'] = convert_size(os.path.getsize(instance.file.path))
        return DocumentForm(initial=data)
