import os

from braces.views import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import (
    render, redirect, reverse, get_object_or_404, Http404
)
from django.views.generic.list import View

from gwml2.forms.download_request import DownloadRequestForm
from gwml2.models.download_request import DownloadRequest


class DownloadRequestFormView(LoginRequiredMixin, View):
    template_name = 'download/form.html'

    def get(self, request, *args, **kwargs):
        user = request.user
        name = user.first_name if user else None
        surname = user.last_name if user else None
        email = user.email if user else None
        organisation = user.organization if user else None
        position = user.position if user else None
        context = {
            'form': DownloadRequestForm(
                instance=DownloadRequest(
                    name=name, surname=surname, email=email,
                    organisation=organisation, position=position
                )
            )
        }
        return render(
            request, self.template_name, context
        )

    def post(self, request, *args, **kwargs):
        form = DownloadRequestForm(request.POST)
        if form.is_valid():
            download_request = form.save(commit=False)
            countries = form.cleaned_data['countries']
            download_request.save()
            download_request.countries.add(*countries)
            download_request.generate_file()
            return redirect(
                reverse(
                    "well_download_request_download",
                    args=[str(download_request.uuid)]
                )
            )
        return render(request, self.template_name, {"form": form})


class DownloadRequestDownloadView(View):
    template_name = 'download/download-page.html'

    def get(self, request, uuid, *args, **kwargs):
        download_request = get_object_or_404(DownloadRequest, uuid=uuid)
        file = download_request.file()
        if not file:
            return redirect("well_download_request_not_exist")
        return render(
            request, self.template_name, {
                'uuid': uuid
            }
        )


class DownloadRequestDownloadFile(View):
    def get(self, request, uuid, *args, **kwargs):
        download_request = get_object_or_404(DownloadRequest, uuid=uuid)
        file = download_request.file()
        if not file or not os.path.exists(file):
            raise Http404("File does not exist")
        with open(file, 'rb') as fh:
            response = HttpResponse(
                fh.read(), content_type="application/zip"
            )
            response['Content-Disposition'] = (
                    'inline; filename=' + os.path.basename(file)
            )
        os.remove(file)
        return response


class DownloadRequestDownloadNotExist(View):
    template_name = 'download/not-exist.html'

    def get(self, request, *args, **kwargs):
        return render(
            request, self.template_name, {}
        )
