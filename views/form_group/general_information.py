from gwml2.forms import (
    GeneralInformationForm,
    DocumentForm,
)
from gwml2.models.well import WellDocument
from gwml2.views.form_group.form_group import FormGroupGet, FormGroupCreate


class GeneralInformationGetForms(FormGroupGet):
    """ Collection form for general information section """

    def get(self):
        """ return forms in dictionary
        :return: dictionary of forms
        :rtype: dict
        """
        documents = []
        for document in self.well.welldocument_set.all():
            documents.append(DocumentForm.make_from_instance(document))
        return {
            # general_information
            'general_information': GeneralInformationForm.make_from_instance(
                self.well),
            'document': DocumentForm(),  # manytomany form
            'documents': documents,  # manytomany data
        }


class GeneralInformationCreateForm(FormGroupCreate):
    """ Collection form for general information section """
    form = None
    documents = []

    def create(self):
        """ create form from data
        """
        self.form = self._make_form(
            self.well, GeneralInformationForm,
            self.data['general_information'])
        for document in self.data['documents']:
            well_doc = WellDocument.objects.get(
                id=document['id_doc']) if document['id_doc'] else WellDocument()
            if not well_doc.well_id:
                well_doc.well = self.well

            self.documents.append(
                self._make_form(well_doc, DocumentForm, document)
            )

    def save(self):
        """ save all available data """
        self.form.save()
        for document in self.documents:
            document.save()
