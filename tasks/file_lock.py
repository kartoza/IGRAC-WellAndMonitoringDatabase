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
    folder = os.path.join(settings.GWML2_FOLDER, 'locks')
    os.makedirs(folder, exist_ok=True)
    lock_path = os.path.join(folder, lock_filename)

    lockfile = None
    try:
        lockfile = open(lock_path, 'w')
        fcntl.flock(lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
        logger.info(f'{lock_filename}: Lock acquired. Running.')
        yield lockfile

    except BlockingIOError:
        logger.info(f"{lock_filename}: Task is already running. Skipping.")
        # Safe to raise runtime error

    except Exception as e:
        logger.exception(f"Failed to acquire file lock {lock_filename}: {e}")
        raise

    finally:
        if lockfile:
            try:
                fcntl.flock(lockfile, fcntl.LOCK_UN)
                logger.info(f'{lock_filename}: Lock released.')
                os.remove(lock_path)
                logger.info(f'{lock_filename}: Lock file deleted.')
            except Exception as e:
                logger.error(
                    f"Error during lock cleanup for {lock_filename}: {e}")
