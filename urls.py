# coding=utf-8
"""Urls for gwml2 apps."""

from django.conf.urls import url
from gwml2.api.upload_progress import get_progress_upload
from gwml2.views.well_uploader import WellUploadView
from gwml2.views.well import WellListView, WellUpdateView


urlpatterns = [
    url(r'^well_upload/$',
        view=WellUploadView.as_view(),
        name='well_upload_view'),
    url(r'^progress_upload/$',
        view=get_progress_upload,
        name='progress_upload'),
    url(r'^well_list/$',
        view=WellListView.as_view(),
        name='well_list_view'),
    url(r'^well_update/(?P<pk>[\w-]+)/$',
        view=WellUpdateView.as_view(),
        name='well_update_view')
]
