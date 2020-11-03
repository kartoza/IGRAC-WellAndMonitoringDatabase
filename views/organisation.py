from django.core.exceptions import PermissionDenied
from django.views.generic.edit import UpdateView
from gwml2.forms.organisation import OrganisationForm
from gwml2.models.well_management.organisation import Organisation


class OrganisationFormView(UpdateView):
    model = Organisation
    template_name = 'well_organisation.html'
    form_class = OrganisationForm
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(OrganisationFormView, self).get_context_data(**kwargs)
        if not self.object.is_admin(self.request.user):
            raise PermissionDenied('You do not have permission.')
        return context
