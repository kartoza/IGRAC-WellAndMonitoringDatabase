from celery import current_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


class State(object):
    PROGRESS = 'PROGRESS'


def update_progress(process_percent):
    current_task.update_state(
        state=State.PROGRESS,
        meta={'process_percent': process_percent})
    logger.debug('Progress {}%'.format(process_percent))
