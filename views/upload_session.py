from pyexcel_xls import get_data as xls_get
from pyexcel_xlsx import get_data as xlsx_get

from django.core.exceptions import PermissionDenied
from django.views.generic.detail import DetailView
from gwml2.models.upload_session import (
    UploadSession,
    UPLOAD_SESSION_CATEGORY_WELL_UPLOAD,
    UPLOAD_SESSION_CATEGORY_MONITORING_UPLOAD
)
from gwml2.tasks.uploader.base import BaseUploader


class UploadSessionDetailView(DetailView):
    model = UploadSession
    template_name = 'upload_session/detail.html'

    def get_context_data(self, **kwargs):
        context = super(UploadSessionDetailView, self).get_context_data(**kwargs)
        if self.object.uploader != self.request.user.id:
            raise PermissionDenied('You do not have permission.')
        # construct excel
        excel = {}
        for row_status in self.object.uploadsessionrowstatus_set.order_by('row'):
            # create header
            if not excel or row_status.sheet_name not in excel:
                _file = self.object.upload_file.path
                sheet = None
                if str(_file).split('.')[-1] == 'xls':
                    sheet = xls_get(_file, column_limit=20)
                elif str(_file).split('.')[-1] == 'xlsx':
                    sheet = xlsx_get(_file, column_limit=20)
                if sheet:
                    sheet_records = sheet[row_status.sheet_name][:BaseUploader.START_ROW]
                    excel[row_status.sheet_name] = {
                        'header': sheet_records,
                        'size': len(sheet_records[0]),
                        'body': {},
                        'id': row_status.sheet_name.replace(' ', '_')
                    }
            try:
                excel[row_status.sheet_name]['body'][row_status.row]
            except KeyError:
                excel[row_status.sheet_name]['body'][row_status.row] = [''] * excel[row_status.sheet_name]['size']

            excel[row_status.sheet_name]['body'][row_status.row][row_status.column] = row_status.note if row_status.note else 'Skipped'
        context['excel'] = excel
        return context
