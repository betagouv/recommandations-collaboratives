from celery import shared_task


@shared_task
def empty_task():
    # TODO: for debug purpose, remove this later
    pass
