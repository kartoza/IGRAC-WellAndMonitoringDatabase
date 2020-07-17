# coding=utf-8
"""Urls for igrac apps."""

from django.conf.urls import url
from gwml2.api.upload_progress import get_progress_upload
from gwml2.views.well_uploader import WellUploadView

urlpatterns = [
    url(r'^well_upload/$',
        view=WellUploadView.as_view(),
        name='well_upload_view'),
    url(r'^progress_upload/$',
        view=get_progress_upload,
        name='progress_upload'),
]
