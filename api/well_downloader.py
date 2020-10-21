from django.http import JsonResponse
from django.views.generic.base import View
from gwml2.tasks.download_well import download_well


class WellDownloader(View):
    def get(self, request, *args, **kwargs):
        """
        Download a well as file
        """
        filters = {

        }
        job = download_well.delay(filters)
        request.session['task_id'] = job.id
        return JsonResponse({
            'task_id': job.id
        })
