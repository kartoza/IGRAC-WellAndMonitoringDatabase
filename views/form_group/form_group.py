import json
from gwml2.models.well import (Well)


class FormNotValid(Exception):
    def __init__(self, error):
        super(Exception, self).__init__(error)
        self.errors = error


class FormGroupGet(object):
    """ Collection form for general information section """

    def __init__(self, well):
        """
        :param well:
        :type well : Well
        """
        self.well = well

    def get(self):
        """ return forms in dictionary
        :return: dictionary of forms
        :rtype: dict
        """
        raise NotImplementedError


class FormGroupCreate(object):
    """ Collection form for general information section """
    form = None
    elevation_form = None

    def __init__(self, well, data, files):
        """
        :param well:
        :type well : Well
        """
        self.form = None
        self.elevation_form = None

        self.well = well
        self.data = data
        self.files = files
        self.create()

    # This is for creating form from data
    def _make_form(self, instance, form, data):
        """ make form from data
        :rtype: ModelForm
        """
        form = form.make_from_data(
            instance, data, self.files)
        if not form.is_valid():
            raise FormNotValid(json.dumps(form.errors))
        return form

    def create(self):
        """ create form from data
        """
        raise NotImplementedError

    def save(self):
        """ save all available data """
        raise NotImplementedError
