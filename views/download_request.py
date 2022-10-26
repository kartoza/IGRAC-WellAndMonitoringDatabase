import os

from django.http import HttpResponse
from django.shortcuts import (
    render, redirect, reverse, get_object_or_404, Http404
)
from django.views.generic.list import View

from gwml2.forms.download_request import DownloadRequestForm
from gwml2.models.download_request import (
    DownloadRequest, WELL_AND_MONITORING_DATA
)
from gwml2.models.general import Country
from igrac.models.profile import IgracProfile


class DownloadRequestFormView(View):
    template_name = 'download/form.html'

    def get(self, request, *args, **kwargs):
        user = None
        if request.user.is_authenticated:
            user = request.user
        first_name = user.first_name if user else None
        last_name = user.last_name if user else None
        email = user.email if user else None
        organization = user.organization if user else None
        country = user.country if user else None
        organization_types = None
        try:
            organization_types = [
                _type.strip()
                for _type in user.igracprofile.organization_types.split(',')
            ]
        except (AttributeError, IgracProfile.DoesNotExist):
            pass
        if country:
            try:
                country = Country.objects.get(code=country)
            except Country.DoesNotExist:
                country = None
        data_type = request.GET.get('data_type', WELL_AND_MONITORING_DATA)
        context = {
            'form': DownloadRequestForm(
                instance=DownloadRequest(
                    first_name=first_name,
                    last_name=last_name, email=email,
                    organization=organization, country=country,
                    organization_types=organization_types,
                    data_type=data_type
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
            if request.user.is_authenticated:
                download_request.user_id = request.user.id
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
