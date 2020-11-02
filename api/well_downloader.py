import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from django.utils.decorators import method_decorator
from gwml2.tasks.download_well import download_well


class WellDownloader(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(WellDownloader, self).dispatch(request, *args, **kwargs)

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

    def post(self, request, *args, **kwargs):
        """
        Download a well as file
        """
        data = json.loads(request.body)
        job = download_well.delay(data)
        request.session['task_id'] = job.id
        return JsonResponse({
            'task_id': '20'
        })
