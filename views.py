import json
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.views.generic import FormView
from django.conf import settings
from pyexcel_xls import get_data as xls_get
from pyexcel_xlsx import get_data as xlsx_get
from .forms import CsvWellForm
from gwml2.tasks import process_excel
from celery.result import AsyncResult


def get_progress_upload(request):
    """A view to return progress of the upload to user."""

    if request.is_ajax():
        if 'task_id' in request.POST.keys() and request.POST['task_id']:
            task_id = request.POST['task_id']
            print('task id')
            print(task_id)
            task = AsyncResult(task_id)
            data = task.info
        else:
            data = 'No task_id in the request'
    else:
        data = 'This is not an ajax request'

    json_data = json.dumps(data)
    return JsonResponse({'data': json_data})


class ExcelUploadView(FormView):
    """Upload excel well view.
    """

    context_object_name = 'csvupload'
    form_class = CsvWellForm
    template_name = 'upload_well_csv.html'

    def get_success_url(self):
        """Define the redirect URL.

       :returns: URL
       :rtype: HttpResponse
       """

        return reverse('excel_upload_view')

    def get_context_data(self, **kwargs):
        """Get the context data which is passed to a template.

        :param kwargs: Any arguments to pass to the superclass.
        :type kwargs: dict

        :returns: Context data which will be passed to the template.
        :rtype: dict
        """

        context = super(
            ExcelUploadView, self).get_context_data(**kwargs)
        try:
            context['task_id'] = self.request.session['task_id']
        except KeyError:
            context['task_id'] = None
        return context

    def get_form_kwargs(self):
        """Get keyword arguments from form.

        :returns keyword argument from the form
        :rtype: dict
        """

        kwargs = super(ExcelUploadView, self).get_form_kwargs()
        return kwargs

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        """Get form instance from upload.

          :returns: URL
          :rtype: HttpResponse
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        gw_location_file = request.FILES.get('gw_location_file')
        gw_level_file = request.FILES.get('gw_level_file')
        location_records = None
        level_records = None

        if form.is_valid():
            if gw_location_file:
                gw_location_file.seek(0)
                if str(gw_location_file).split('.')[-1] == "xls":
                    sheet = xls_get(gw_location_file, column_limit=4)
                elif str(gw_location_file).split('.')[-1] == "xlsx":
                    sheet = xlsx_get(gw_location_file, column_limit=4)
                sheetname = next(iter(sheet))
                location_records = sheet[sheetname]

            if gw_level_file:
                gw_level_file.seek(0)
                if str(gw_level_file).split('.')[-1] == "xls":
                    sheet = xls_get(gw_level_file, column_limit=4)
                elif str(gw_level_file).split('.')[-1] == "xlsx":
                    sheet = xlsx_get(gw_level_file, column_limit=4)
                sheetname = next(iter(sheet))
                level_records = sheet[sheetname]

            print(settings.CELERY_TASK_ALWAYS_EAGER)
            job = process_excel.delay(location_records, level_records)
            request.session['task_id'] = job.id
            return self.form_valid(form)

        else:
            return self.form_invalid(form)

