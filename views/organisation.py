from braces.views import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from gwml2.forms.organisation import OrganisationForm
from gwml2.models.well_management.organisation import Organisation


class OrganisationFormView(LoginRequiredMixin, UpdateView):
    model = Organisation
    template_name = 'organisation/edit.html'
    form_class = OrganisationForm

    def get_context_data(self, **kwargs):
        context = super(OrganisationFormView, self).get_context_data(**kwargs)
        if not self.object.is_admin(self.request.user):
            raise PermissionDenied('You do not have permission.')
        return context

    def get_success_url(self):
        return reverse('organisation_list')


class OrganisationListView(LoginRequiredMixin, ListView):
    model = Organisation
    template_name = 'organisation/list.html'

    def get_queryset(self):
        queryset = super(OrganisationListView, self).get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(admins__contains=[self.request.user.id])
        return queryset
