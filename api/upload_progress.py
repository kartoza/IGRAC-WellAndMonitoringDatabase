from celery.result import AsyncResult
from django.http import JsonResponse, HttpResponseBadRequest


def get_progress_upload(request):
    """
    An API to return progress of the upload to user.
    """

    def delete_session(data):
        if 'task_id' in request.session:
            if data and data['process_percent'] == 100:
                del request.session['task_id']
            elif not data:
                del request.session['task_id']

    data = None
    try:
        task_id = request.GET['task_id']
        task = AsyncResult(task_id)
        data = task.result
        if not data:
            raise TypeError
        delete_session(data)
        return JsonResponse(data)
    except KeyError:
        return HttpResponseBadRequest('task_id is required')
    except TypeError:
        delete_session(data)
        return HttpResponseBadRequest('task_id is not found')
