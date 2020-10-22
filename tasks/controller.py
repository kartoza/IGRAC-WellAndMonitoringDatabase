from celery import current_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


class State(object):
    PROGRESS = 'PROGRESS'
    FINISH = 'FINISH'


def update_progress(process_percent, data={}):
    data.update({
        'process_percent': process_percent
    })
    current_task.update_state(
        state=State.FINISH if process_percent == 100 else State.PROGRESS,
        meta=data
    )
    logger.debug('Progress {}%'.format(process_percent))
