from braces.views import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import FormView

from gwml2.forms import CsvWellForm
from gwml2.models.upload_session import (
    UploadSession,
    UPLOAD_SESSION_CATEGORY_WELL_UPLOAD,
    UPLOAD_SESSION_CATEGORY_MONITORING_UPLOAD,
    UPLOAD_SESSION_CATEGORY_DRILLING_CONSTRUCTION_UPLOAD
)
from gwml2.utilities import get_organisations_as_editor


class WellUploadView(LoginRequiredMixin, FormView):
    """ Upload excel well view.
    """

    context_object_name = 'csvupload'
    form_class = CsvWellForm
    template_name = 'upload_session/form.html'

    def get_success_url(self):
        """Define the redirect URL.

       :returns: URL
       :rtype: HttpResponse
       """

        return reverse('well_upload_history_view')

    def post(self, request, *args, **kwargs):
        """Get form instance from upload.

          :returns: URL
          :rtype: HttpResponse
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        gw_well_file = request.FILES.get('gw_well_file')
        gw_monitoring_file = request.FILES.get('gw_well_monitoring_file')
        gw_well_drilling_and_construction_file = request.FILES.get(
            'gw_well_drilling_and_construction_file'
        )

        if form.is_valid():
            if gw_well_file:
                upload_session = UploadSession.objects.create(
                    organisation=form.cleaned_data['organisation'],
                    category=UPLOAD_SESSION_CATEGORY_WELL_UPLOAD,
                    upload_file=gw_well_file,
                    uploader=request.user.id,
                    is_adding=form.cleaned_data.get('is_adding', False),
                    is_updating=form.cleaned_data.get('is_updating', False)
                )
            elif gw_monitoring_file:
                upload_session = UploadSession.objects.create(
                    organisation=form.cleaned_data['organisation'],
                    category=UPLOAD_SESSION_CATEGORY_MONITORING_UPLOAD,
                    upload_file=gw_monitoring_file,
                    uploader=request.user.id,
                )
            elif gw_well_drilling_and_construction_file:
                upload_session = UploadSession.objects.create(
                    organisation=form.cleaned_data['organisation'],
                    category=(
                        UPLOAD_SESSION_CATEGORY_DRILLING_CONSTRUCTION_UPLOAD
                    ),
                    upload_file=gw_well_drilling_and_construction_file,
                    uploader=request.user.id,
                )
            else:
                return self.form_invalid(form)

            upload_session.run_in_background()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
