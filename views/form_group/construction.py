from gwml2.forms import (
    ConstructionForm, ConstructionStructureForm
)
from gwml2.models.construction import (
    Construction, ConstructionStructure
)
from gwml2.views.form_group.form_group import FormGroupGet, FormGroupCreate


class ConstructionGetForms(FormGroupGet):
    """ Collection form for general information section """

    def get(self):
        """ return forms in dictionary
        :return: dictionary of forms
        :rtype: dict
        """
        structures = []
        if self.well.construction:
            for obj in self.well.construction.constructionstructure_set.all():
                structures.append(ConstructionStructureForm.make_from_instance(obj))
        return {
            'construction': ConstructionForm.make_from_instance(
                self.well.construction),
            'structure': ConstructionStructureForm(),
            'structures': structures,
        }


class ConstructionCreateForm(FormGroupCreate):
    """ Collection form for general information section """
    structures = []

    def create(self):
        """ create form from data
        """
        self.structures = []
        if self.data.get('construction', None):
            self.form = self._make_form(
                self.well.construction if self.well.construction else Construction(),
                ConstructionForm, self.data['construction'])
            if self.data['construction'].get('structure', None):
                for structure in self.data['construction']['structure']:
                    obj = ConstructionStructure.objects.get(
                        id=structure['id']) if structure['id'] else ConstructionStructure()

                    self.structures.append(
                        self._make_form(
                            obj, ConstructionStructureForm, structure
                        )
                    )

    def save(self):
        """ save all available data """
        if self.form:
            self.form.save()
            for structure in self.structures:
                structure.instance.construction = self.form.instance
                structure.save()
            self.well.construction = self.form.instance
