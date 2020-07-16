# coding=utf-8
"""Urls for igrac apps."""

from django.conf.urls import url
from .views import ExcelUploadView, get_progress_upload


urlpatterns = [
    url(r'^well_upload/$',
        view=ExcelUploadView.as_view(),
        name='excel_upload_view'),
    url(r'^progress_upload/$',
        view=get_progress_upload,
        name='progress_upload'),
]
