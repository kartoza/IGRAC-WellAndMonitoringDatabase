# coding=utf-8
"""Urls for igrac apps."""

from django.conf.urls import url
from django.urls import include
from gwml2.api.upload_progress import get_progress_upload
from gwml2.views.groundwater_form import WellFormView
from gwml2.views.well_uploader import WellUploadView

well_urls = [
    url(r'^edit',
        view=WellFormView.as_view(),
        name='well_form'),
]

urlpatterns = [
    url(r'^well-upload',
        view=WellUploadView.as_view(),
        name='well_upload_view'),
    url(r'^progress-upload',
        view=get_progress_upload,
        name='progress_upload'),
    url(r'^well/(?P<id>\d+)/', include(well_urls)),
]
