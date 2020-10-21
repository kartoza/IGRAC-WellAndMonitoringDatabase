from celery.result import AsyncResult
from django.http import JsonResponse, HttpResponseBadRequest, Http404
from django.views.generic.base import View


class TaskProgress(View):
    """
    API to return progress of a task
    """

    def delete_session(self, data):
        if 'task_id' in self.request.session:
            if data and data['process_percent'] == 100:
                del self.request.session['task_id']
            elif not data:
                del self.request.session['task_id']

    def get(self, request, task_id, *args, **kwargs):
        data = None
        try:
            task = AsyncResult(task_id)
            data = task.result
            if not data:
                raise TypeError
            self.delete_session(data)
            return JsonResponse(data)
        except KeyError:
            return HttpResponseBadRequest('task_id is required')
        except TypeError:
            self.delete_session(data)
            raise Http404('task_id is not found')
