import json

from django.http import HttpResponse
from django.shortcuts import (
    render, redirect, reverse, get_object_or_404
)
from django.views.generic.list import View

from gwml2.forms.download_request import (
    DownloadRequestForm, DownloadRequestByIdsForm
)
from gwml2.models.download_request import (
    DownloadRequest, GGMN
)
from gwml2.models.general import Country
from gwml2.tasks.downloader import prepare_download_file
from igrac.models.profile import IgracProfile


USER_INFO_SESSION_KEY = 'download_user_info'
USER_INFO_FIELDS = [
    'email', 'first_name', 'last_name', 'organization', 'organization_types'
]


def _save_user_info_to_session(request, form):
    """Cache personal fields from a valid form into the session."""
    info = {f: form.cleaned_data.get(f) for f in USER_INFO_FIELDS}
    country = form.cleaned_data.get('country')
    info['country_id'] = country.id if country else None
    request.session[USER_INFO_SESSION_KEY] = info


def _get_user_info_from_session(request):
    """Return cached personal fields, resolving country FK."""
    info = request.session.get(USER_INFO_SESSION_KEY, {})
    country = None
    country_id = info.get('country_id')
    if country_id:
        try:
            country = Country.objects.get(id=country_id)
        except Country.DoesNotExist:
            pass
    return {**{f: info.get(f) for f in USER_INFO_FIELDS}, 'country': country}


class DownloadRequestFormView(View):
    template_name = 'download/form.html'

    def get(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
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

        # Fall back to session cache for any fields not covered by the profile
        cached = _get_user_info_from_session(request)
        first_name = first_name or cached.get('first_name')
        last_name = last_name or cached.get('last_name')
        email = email or cached.get('email')
        organization = organization or cached.get('organization')
        organization_types = organization_types or cached.get('organization_types')
        country = country or cached.get('country')

        data_type = request.GET.get('data_type', GGMN)
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
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = DownloadRequestForm(request.POST)
        if form.is_valid():
            download_request = form.save(commit=False)
            countries = form.cleaned_data['countries']
            organisations = form.cleaned_data['organisations']
            if request.user.is_authenticated:
                download_request.user_id = request.user.id
            download_request.save()
            download_request.countries.add(*countries)
            download_request.organisations.add(*organisations)
            _save_user_info_to_session(request, form)
            prepare_download_file.delay(download_request.id)
            return redirect(
                reverse(
                    "well_download_request_download",
                    args=[str(download_request.uuid)]
                )
            )
        return render(request, self.template_name, {"form": form})


class DownloadRequestByIdsInitiateView(View):
    """Accept wells_id + data_type from frontend, store in session, redirect to form."""

    def post(self, request, *args, **kwargs):
        wells_id = request.POST.getlist('wells_id')
        data_type = request.POST.get('data_type', GGMN)
        try:
            wells_id = [int(i) for i in wells_id if i]
        except (ValueError, TypeError):
            return HttpResponse('Invalid wells_id', status=400)
        request.session['download_by_ids'] = {
            'wells_id': wells_id,
            'data_type': data_type,
        }
        return redirect(reverse('well_download_request_by_ids'))


class DownloadRequestByIdsFormView(View):
    """Handle download requests for a specific list of well IDs."""

    template_name = 'download/form-by-ids.html'

    def _get_session_data(self, request):
        return request.session.get('download_by_ids', {})

    def get(self, request, *args, **kwargs):
        session = self._get_session_data(request)
        wells_id = session.get('wells_id', [])
        data_type = session.get('data_type', GGMN)
        cached = _get_user_info_from_session(request)
        form = DownloadRequestByIdsForm(
            instance=DownloadRequest(
                data_type=data_type,
                email=cached.get('email'),
                first_name=cached.get('first_name'),
                last_name=cached.get('last_name'),
                organization=cached.get('organization'),
                organization_types=cached.get('organization_types'),
                country=cached.get('country'),
            )
        )
        return render(request, self.template_name, {
            'form': form,
            'wells_id': wells_id,
            'wells_count': len(wells_id),
            'data_type': data_type,
        })

    def post(self, request, *args, **kwargs):
        form = DownloadRequestByIdsForm(request.POST)
        wells_id = request.POST.getlist('wells_id')
        data_type = request.POST.get('data_type', GGMN)
        if form.is_valid():
            download_request = form.save(commit=False)
            if request.user.is_authenticated:
                download_request.user_id = request.user.id
            download_request.save()
            _save_user_info_to_session(request, form)
            prepare_download_file.delay(download_request.id)
            return redirect(
                reverse(
                    'well_download_request_download',
                    args=[str(download_request.uuid)]
                )
            )
        return render(request, self.template_name, {
            'form': form,
            'wells_id': wells_id,
            'wells_count': len(wells_id),
            'data_type': data_type,
        })


class DownloadRequestDownloadView(View):
    template_name = 'download/download-page.html'

    def get(self, request, uuid, *args, **kwargs):
        download_request = get_object_or_404(DownloadRequest, uuid=uuid)
        file = download_request.file()
        return render(
            request, self.template_name, {
                'uuid': uuid,
                'is_ready': download_request.is_ready,
                'is_error': download_request.is_error,
                'note': download_request.note,
                'has_file': file is not None,
                'download_request': download_request,
            }
        )


class DownloadRequestDownloadStatus(View):

    def get(self, request, uuid, *args, **kwargs):
        download_request = get_object_or_404(DownloadRequest, uuid=uuid)
        return HttpResponse(
            json.dumps({
                'is_ready': download_request.is_ready,
                'is_error': download_request.is_error,
                'note': download_request.note,
            }),
            content_type="application/json"
        )
