# coding=utf-8
"""Urls for igrac apps."""

from django.urls import include, re_path
from django.views.generic import TemplateView

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
from gwml2.api.upload_session import (
    UploadSessionApiView, UploadSessionStopApiView, UploadSessionListApiView
)
from gwml2.api.user import UserAutocompleteAPI, UserUUIDAPI
from gwml2.api.well_deletion import WellDeletionAPI
from gwml2.api.well_measurement import WellLevelMeasurementData
from gwml2.api.well_relation import (
    WellRelationDeleteView,
    WellRelationListView,
    WellMeasurementDataView
)
from gwml2.views.admin.delete_selected_confirmation_background import (
    DeleteWellPostView, DeleteWellProgressView
)
from gwml2.views.download_request import (
    DownloadRequestFormView,
    DownloadRequestDownloadView,
    DownloadRequestDownloadStatus
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
    re_path(
        r'^delete',
        view=WellRelationDeleteView.as_view(),
        name='well-relation-delete'
    ),
]
well_detail_urls = [
    re_path(
        r'^(?P<model>[\w\+%_& ]+)/(?P<model_id>\d+)/',
        include(well_relation)
    ),
    re_path(
        r'^(?P<model>[\w\+%_& ]+)/list$',
        WellRelationListView.as_view(),
        name='well-relation-list'
    ),
    re_path(
        r'^measurements/WellLevelMeasurement/chart-data',
        WellLevelMeasurementData.as_view(),
        name='well-level-measurement-chart-data'
    ),
    re_path(
        r'^measurements/(?P<model>[\w\+%_& ]+)/data$',
        WellMeasurementDataView.as_view(),
        name='well-measurement-chart-data'
    ),
    re_path(
        r'^measurements/(?P<model>[\w\+%_& ]+)/chart/iframe$',
        MeasurementChartIframe.as_view(),
        name='well-measurement-chart-iframe'
    ),
    re_path(
        r'^measurements/(?P<model>[\w\+%_& ]+)/chart$',
        MeasurementChart.as_view(),
        name='well-measurement-chart'
    ),
    re_path(
        r'^edit',
        view=WellFormView.as_view(),
        name='well_form'
    ),
    re_path(
        r'^',
        view=WellView.as_view(),
        name='well_view'
    ),
]

well_url = [
    re_path(
        r'^download/(?P<uuid>[0-9a-f-]+)/status$',
        view=DownloadRequestDownloadStatus.as_view(),
        name='well_download_request_status'
    ),
    re_path(
        r'^download/(?P<uuid>[0-9a-f-]+)$',
        view=DownloadRequestDownloadView.as_view(),
        name='well_download_request_download'
    ),
    re_path(
        r'^download$',
        view=DownloadRequestFormView.as_view(),
        name='well_download_request'
    ),
    re_path(
        r'^create/',
        view=WellFormCreateView.as_view(),
        name='well_create'
    ),
    re_path(r'^(?P<id>\d+)/', include(well_detail_urls)),
]

organisation_url = [
    re_path(
        r'^(?P<pk>\d+)/edit',
        view=OrganisationFormView.as_view(),
        name='organisation_form'
    ),
    re_path(
        r'^',
        view=OrganisationListView.as_view(),
        name='organisation_list'
    )
]

user_url = [
    re_path(
        r'^uuid/',
        view=UserUUIDAPI.as_view(),
        name='user_uuid'
    )
]

api_minimized_url = [
    re_path(
        r'^create',
        view=WellCreateMinimizedAPI.as_view(),
        name='well_create_api'
    ),
    re_path(
        r'^(?P<id>\d+)/edit',
        view=WellEditMinimizedAPI.as_view(),
        name='well_edit_api'
    ),
    re_path(
        r'^(?P<id>\d+)/(?P<measurement_type>[\w\+%_& ]+)',
        view=WellMeasurementListMinimizedAPI.as_view(),
        name='well_measurement_list_minimized_api'
    ),
    re_path(
        r'^',
        view=WellListMinimizedAPI.as_view(),
        name='well_list_minimized_api'
    ),
]
api_url = [
    re_path(r'^well/minimized/', include(api_minimized_url)),

    # autocomplete
    re_path(
        r'^organisation/autocomplete',
        view=OrganisationAutocompleteAPI.as_view(),
        name='organisation_autocomplete'
    ),
    re_path(
        r'^user/autocomplete',
        view=UserAutocompleteAPI.as_view(),
        name='user_autocomplete'
    ),
    re_path(
        r'^country/autocomplete',
        view=CountryAutocompleteAPI.as_view(),
        name='country_autocomplete'
    ),
]
upload_session_url = [
    re_path(
        r'^list',
        view=UploadSessionListApiView.as_view(),
        name='upload_session_list'
    ),
    re_path(
        r'^'
        r'(?P<token>\b[0-9a-f]{8}\b-[0-9a-f]{4}-'
        r'[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}\b)/stop',
        view=UploadSessionStopApiView.as_view(),
        name='upload_session_stop'
    ),
    re_path(
        r'^'
        r'(?P<token>\b[0-9a-f]{8}\b-[0-9a-f]{4}-'
        r'[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}\b)/',
        view=UploadSessionApiView.as_view(),
        name='upload_session_progress'
    ),
    re_path(
        r'^(?P<pk>\d+)/detail',
        view=UploadSessionDetailView.as_view(),
        name='upload_session_detail'
    ),
]

urlpatterns = [
    re_path(
        r'^token-auth',
        view=TokenAuth.as_view(),
        name='gwml2-token-aut'
    ),
    re_path(
        r'^batch-upload/history',
        TemplateView.as_view(template_name='upload_session/history.html'),
        name='well_upload_history_view'
    ),
    re_path(
        r'^batch-upload',
        view=WellUploadView.as_view(),
        name='well_upload_view'
    ),
    re_path(
        r'^progress-upload',
        view=get_progress_upload,
        name='progress_upload'
    ),
    re_path(
        r'^task/(?P<task_id>.+)/progress/',
        view=TaskProgress.as_view(),
        name='task_progress'
    ),
    re_path(
        r'^delete/well/progress/(?P<uuid>[0-9a-f-]+)/data',
        view=WellDeletionAPI.as_view(),
        name='delete-well-progress-data'
    ),
    re_path(
        r'^delete/well/progress/(?P<uuid>[0-9a-f-]+)',
        view=DeleteWellProgressView.as_view(),
        name='delete-well-progress-view'
    ),
    re_path(
        r'^delete/well/',
        view=DeleteWellPostView.as_view(),
        name='delete-well-confirmation-view'
    ),
    re_path(r'^api/', include(api_url)),
    re_path(r'^record/', include(well_url)),
    re_path(r'^user/', include(user_url)),
    re_path(r'^organisation/', include(organisation_url)),
    re_path(r'^upload-session/', include(upload_session_url)),
]
