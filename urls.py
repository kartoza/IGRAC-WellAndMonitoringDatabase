# coding=utf-8
"""Urls for igrac apps."""

from django.conf.urls import url
from django.urls import include

from gwml2.api.authentication import TokenAuth
from gwml2.api.country import CountryAutocompleteAPI
from gwml2.api.mobile.minimized_well import (
    WellListMinimizedAPI,
    WellMeasurementListMinimizedAPI
)
from gwml2.api.mobile.well import WellCreateMinimizedAPI, WellEditMinimizedAPI
from gwml2.api.organisation import OrganisationAutocompleteAPI
from gwml2.api.task_progress import TaskProgress
from gwml2.api.upload_progress import get_progress_upload
from gwml2.api.upload_session import UploadSessionApiView
from gwml2.api.user import (UserAutocompleteAPI, UserUUIDAPI)
from gwml2.api.well_measurement import WellLevelMeasurementData
from gwml2.api.well_relation import (
    WellRelationDeleteView,
    WellRelationListView,
    WellMeasurementDataView
)
from gwml2.views.download_request import (
    DownloadRequestFormView,
    DownloadRequestDownloadNotExist,
    DownloadRequestDownloadView,
    DownloadRequestDownloadFile
)
from gwml2.views.groundwater_form import (
    WellView, WellFormView,
    WellFormCreateView
)
from gwml2.views.organisation import OrganisationFormView, OrganisationListView
from gwml2.views.plugins.measurements_chart import (
    MeasurementChart,
    MeasurementChartIframe
)
from gwml2.views.upload_session import UploadSessionDetailView
from gwml2.views.well_uploader import WellUploadView

well_relation = [
    url(r'^delete',
        view=WellRelationDeleteView.as_view(),
        name='well-relation-delete'),
]
well_detail_urls = [
    url(r'^(?P<model>[\w\+%_& ]+)/(?P<model_id>\d+)/', include(well_relation)),
    url(r'^(?P<model>[\w\+%_& ]+)/list', WellRelationListView.as_view(),
        name='well-relation-list'),
    url(r'^measurements/WellLevelMeasurement/chart-data',
        WellLevelMeasurementData.as_view(),
        name='well-level-measurement-chart-data'),
    url(r'^measurements/(?P<model>[\w\+%_& ]+)/data',
        WellMeasurementDataView.as_view(),
        name='well-measurement-chart-data'),
    url(r'^measurements/(?P<model>[\w\+%_& ]+)/chart/iframe',
        MeasurementChartIframe.as_view(),
        name='well-measurement-chart-iframe'),
    url(r'^measurements/(?P<model>[\w\+%_& ]+)/chart',
        MeasurementChart.as_view(),
        name='well-measurement-chart'),
    url(r'^edit',
        view=WellFormView.as_view(),
        name='well_form'),
    url(r'^',
        view=WellView.as_view(),
        name='well_view'),
]

well_url = [
    url(r'^download-request/not-exist$',
        view=DownloadRequestDownloadNotExist.as_view(),
        name='well_download_request_not_exist'),
    url(r'^download-request/(?P<uuid>[0-9a-f-]+)/file$',
        view=DownloadRequestDownloadFile.as_view(),
        name='well_download_request_file'),
    url(r'^download-request/(?P<uuid>[0-9a-f-]+)$',
        view=DownloadRequestDownloadView.as_view(),
        name='well_download_request_download'),
    url(r'^download-request$',
        view=DownloadRequestFormView.as_view(),
        name='well_download_request'),
    url(r'^create/',
        view=WellFormCreateView.as_view(),
        name='well_create'),
    url(r'^(?P<id>\d+)/', include(well_detail_urls)),
]

organisation_url = [
    url(r'^(?P<pk>\d+)/edit',
        view=OrganisationFormView.as_view(),
        name='organisation_form'),
    url(r'^',
        view=OrganisationListView.as_view(),
        name='organisation_list')
]

user_url = [
    url(r'^uuid/',
        view=UserUUIDAPI.as_view(),
        name='user_uuid')
]

api_minimized_url = [
    url(r'^create',
        view=WellCreateMinimizedAPI.as_view(),
        name='well_create_api'),
    url(r'^(?P<id>\d+)/edit',
        view=WellEditMinimizedAPI.as_view(),
        name='well_edit_api'),
    url(r'^(?P<id>\d+)/(?P<measurement_type>[\w\+%_& ]+)',
        view=WellMeasurementListMinimizedAPI.as_view(),
        name='well_measurement_list_minimized_api'),
    url(r'^',
        view=WellListMinimizedAPI.as_view(),
        name='well_list_minimized_api'),
]
api_url = [
    url(r'^well/minimized/', include(api_minimized_url)),

    # autocomplete
    url(r'^organisation/autocomplete',
        view=OrganisationAutocompleteAPI.as_view(),
        name='organisation_autocomplete'),
    url(r'^user/autocomplete',
        view=UserAutocompleteAPI.as_view(),
        name='user_autocomplete'),
    url(r'^country/autocomplete',
        view=CountryAutocompleteAPI.as_view(),
        name='country_autocomplete'),
]

urlpatterns = [
    url(r'^token-auth',
        view=TokenAuth.as_view(),
        name='gwml2-token-aut'),
    url(r'^batch-upload',
        view=WellUploadView.as_view(),
        name='well_upload_view'),
    url(r'^progress-upload',
        view=get_progress_upload,
        name='progress_upload'),
    url(r'^task/(?P<task_id>.+)/progress/',
        view=TaskProgress.as_view(),
        name='task_progress'),
    url(r'^api/', include(api_url)),
    url(r'^record/', include(well_url)),
    url(r'^user/', include(user_url)),
    url(r'^organisation/', include(organisation_url)),
    url(r'^upload-session/'
        r'(?P<token>\b[0-9a-f]{8}\b-[0-9a-f]{4}-'
        r'[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}\b)/',
        view=UploadSessionApiView.as_view(),
        name='upload_session_progress'),
    url(r'^upload-session/(?P<pk>\d+)/detail',
        view=UploadSessionDetailView.as_view(),
        name='upload_session_detail'),
]
