import fcntl
import os
from contextlib import contextmanager

from celery.utils.log import get_task_logger
from django.conf import settings

logger = get_task_logger(__name__)


@contextmanager
def file_lock(lock_filename: str):
    """Context manager to acquire a file lock using fcntl (Linux/macOS only).
    If lock cannot be acquired, yields None.

    Usage:
        with file_lock('my.lock') as lockfile:
            if lockfile is None:
                return
            # Do work
    """
    lock_path = os.path.join(settings.MEDIA_ROOT, lock_filename)
    try:
        with open(lock_path, 'w') as lockfile:
            try:
                fcntl.flock(lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
                logger.info(f'{lock_filename}: Running.')
                yield lockfile
            except BlockingIOError:
                logger.info(
                    f"{lock_filename}: Task is already running. Skipping.")
                yield None
    except Exception as e:
        logger.exception(f"Failed to acquire file lock {lock_filename}: {e}")
        yield None
