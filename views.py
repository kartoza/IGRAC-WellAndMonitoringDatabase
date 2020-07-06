from django.db import transaction
from django.contrib.gis.geos import Point
from django.urls import reverse
from django.views.generic import FormView
from django.utils import dateparse
from pyexcel_xls import get_data as xls_get
from pyexcel_xlsx import get_data as xlsx_get
from .forms import CsvWellForm
from gwml2.models.well import GWWell, GWGeologyLog
from gwml2.models.universal import Quantity


class CsvUploadView(FormView):
    """Upload csv well view.
    """

    context_object_name = 'csvupload'
    form_class = CsvWellForm
    template_name = 'upload_well_csv.html'

    def get_success_url(self):
        """Define the redirect URL.

       :returns: URL
       :rtype: HttpResponse
       """

        return reverse('home_igrac')

    def get_context_data(self, **kwargs):
        """Get the context data which is passed to a template.

        :param kwargs: Any arguments to pass to the superclass.
        :type kwargs: dict

        :returns: Context data which will be passed to the template.
        :rtype: dict
        """

        context = super(
            CsvUploadView, self).get_context_data(**kwargs)
        return context

    def get_form_kwargs(self):
        """Get keyword arguments from form.

        :returns keyword argument from the form
        :rtype: dict
        """

        kwargs = super(CsvUploadView, self).get_form_kwargs()
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

        if form.is_valid():
            if gw_location_file:
                gw_location_file.seek(0)
                if str(gw_location_file).split('.')[-1] == "xls":
                    sheet = xls_get(gw_location_file, column_limit=4)
                elif str(gw_location_file).split('.')[-1] == "xlsx":
                    sheet = xlsx_get(gw_location_file, column_limit=4)
                sheetname = next(iter(sheet))
                records = sheet[sheetname]
                for record in records:
                    if record[0].lower() == 'id well':
                        continue

                    point = Point(x=record[3], y=record[2], srid=4326)
                    try:
                        well = GWWell.objects.get(gw_well_name=record[0])
                        well.gw_well_location = point
                        well.gw_well_total_length = record[1]
                        well.save()
                    except GWWell.DoesNotExist:
                        well = GWWell.objects.create(
                            gw_well_name=record[0],
                            gw_well_location=point,
                            gw_well_total_length=record[1]
                        )

            if gw_level_file:
                gw_level_file.seek(0)
                if str(gw_level_file).split('.')[-1] == "xls":
                    sheet = xls_get(gw_level_file, column_limit=4)
                elif str(gw_level_file).split('.')[-1] == "xlsx":
                    sheet = xlsx_get(gw_level_file, column_limit=4)
                sheetname = next(iter(sheet))
                records = sheet[sheetname]
                for record in records:
                    if record[0].lower == 'time':
                        continue

                    try:
                        well = GWWell.objects.get(gw_well_name=record[3])
                        time = dateparse.parse_datetime(record[0])
                        depth = Quantity.objects.create(
                            value=record[2],
                            unit='meter'
                        )
                        well_level_log = GWGeologyLog.objects.create(
                            phenomenon_time=time,
                            result_time=time,
                            gw_level=record[2],
                            reference=record[1],
                            gw_well=well,
                            start_depth=depth,
                            end_depth=depth
                        )
                    except GWWell.DoesNotExist:
                        pass
                pass
            return self.form_valid(form)

        else:
            return self.form_invalid(form)

