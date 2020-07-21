from django.views.generic import ListView, UpdateView
from django.urls import reverse
from gwml2.models.well.gw_well import GWWell
from gwml2.forms import WellUpdateForm
from braces.views import StaffuserRequiredMixin, LoginRequiredMixin


class WellListView(LoginRequiredMixin, ListView):
    """View for list of wells."""

    model = GWWell
    context_object_name = 'wells'
    template_name = 'well/list.html'
    paginate_by = 10

    def get_queryset(self, queryset=None):
        """Get the queryset for this view.

        :param queryset: A query set
        :type queryset: QuerySet

        :returns: Wells.
        :rtype: QuerySet
        """

        if self.queryset is None:
            queryset = GWWell.objects.all().order_by('gw_well_name')
            return queryset
        return self.queryset


class WellUpdateView(StaffuserRequiredMixin, UpdateView):
    """View for updating well."""

    model = GWWell
    form_class = WellUpdateForm
    context_object_name = 'well'
    template_name = 'well/update.html'

    def get_success_url(self):
        """Define the redirect URL.

       :returns: URL
       :rtype: HttpResponse
       """

        return reverse('well_list_view')

    def get_context_data(self, **kwargs):
        """Get the context data which is passed to a template.

        :param kwargs: Any arguments to pass to the superclass.
        :type kwargs: dict

        :returns: Context data which will be passed to the template.
        :rtype: dict
        """

        context = super(WellUpdateView, self).get_context_data(**kwargs)
        return context
