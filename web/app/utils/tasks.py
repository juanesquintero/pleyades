import time
from datetime import datetime
import traceback
from celery import shared_task


@shared_task(ignore_result=False)
def sleep_task(seconds: int) -> datetime:
    for sec in range(seconds):
        print(f'Sleeping for {sec} seconds...')
        time.sleep(1)
    return datetime.now()


@shared_task(ignore_result=False)
def schedule_preparation_task(preparation_id: str) -> None:
    pass


def run_task(function_task, **kwargs) -> None:
    try:
        result = function_task.delay(**kwargs)
        return result
    except Exception as e:
        error = str(e) + '\n' + traceback.format_exc()
        return error
