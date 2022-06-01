import json
from django.db.models import Q
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import FormView

from braces.views import LoginRequiredMixin

from gwml2.forms import CsvWellForm
from gwml2.tasks import well_batch_upload
from gwml2.models.upload_session import (
    UploadSession,
    UPLOAD_SESSION_CATEGORY_WELL_UPLOAD,
    UPLOAD_SESSION_CATEGORY_MONITORING_UPLOAD
)
from gwml2.utilities import get_organisations_as_editor
from gwml2.serializer.upload_session import UploadSessionSerializer


class WellUploadView(LoginRequiredMixin, FormView):
    """ Upload excel well view.
    """

    context_object_name = 'csvupload'
    form_class = CsvWellForm
    template_name = 'upload_well_csv.html'

    def get_success_url(self):
        """Define the redirect URL.

       :returns: URL
       :rtype: HttpResponse
       """

        return reverse('well_upload_view')

    def get_context_data(self, **kwargs):
        """Get the context data which is passed to a template.

        :param kwargs: Any arguments to pass to the superclass.
        :type kwargs: dict

        :returns: Context data which will be passed to the template.
        :rtype: dict
        """

        context = super(
            WellUploadView, self).get_context_data(**kwargs)
        upload_sessions = UploadSession.objects.filter(
            is_canceled=False,
            is_processed=False,
            uploader=self.request.user.id
        )
        if upload_sessions.count() > 0:
            upload_session = upload_sessions[0]
            context['upload_session'] = upload_session
            context['upload_session_file_name'] = (
                upload_session.upload_file.name.split('/')[1]
            )
        MAX = 10
        context['past_upload'] = UploadSessionSerializer(
            UploadSession.objects.filter(
                Q(is_canceled=True) |
                Q(is_processed=True)
            ).filter(
                uploader=self.request.user.id
            )[:MAX], many=True).data
        context['past_upload'] = json.dumps(context['past_upload'])
        return context

    def get_form_kwargs(self):
        """Get keyword arguments from form.

        :returns keyword argument from the form
        :rtype: dict
        """

        kwargs = super(WellUploadView, self).get_form_kwargs()
        kwargs['organisation'] = get_organisations_as_editor(self.request.user)
        return kwargs

    def post(self, request, *args, **kwargs):
        """Get form instance from upload.

          :returns: URL
          :rtype: HttpResponse
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        gw_well_file = request.FILES.get('gw_well_file')
        gw_monitoring_file = request.FILES.get('gw_well_monitoring_file')

        if form.is_valid():
            if gw_well_file:
                upload_session = UploadSession.objects.create(
                    organisation=form.cleaned_data['organisation'],
                    category=UPLOAD_SESSION_CATEGORY_WELL_UPLOAD,
                    upload_file=gw_well_file,
                    uploader=request.user.id,
                    public=form.cleaned_data['public'],
                    downloadable=form.cleaned_data['downloadable']
                )
            elif gw_monitoring_file:
                upload_session = UploadSession.objects.create(
                    organisation=form.cleaned_data['organisation'],
                    category=UPLOAD_SESSION_CATEGORY_MONITORING_UPLOAD,
                    upload_file=gw_monitoring_file,
                    uploader=request.user.id,
                    public=form.cleaned_data['public'],
                    downloadable=form.cleaned_data['downloadable']
                )
            else:
                return self.form_invalid(form)

            well_batch_upload.delay(upload_session.id)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
