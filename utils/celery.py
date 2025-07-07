from celery import current_app


def id_task_is_running(task_id) -> bool:
    """Is task running."""
    if not task_id:
        return False
    try:
        inspector = current_app.control.inspect()
        task_id = task_id
        for state in ('active', 'reserved'):
            tasks = getattr(inspector, state)() or {}
            for task_list in tasks.values():
                if any(task.get("id") == task_id for task in task_list):
                    return True

    except Exception:
        return False
    return False
