import time
from datetime import datetime
from celery import shared_task


@shared_task(ignore_result=False)
def sleep_task(seconds: int) -> datetime:
    for sec in range(seconds):
        print(f'Sleeping for {sec} seconds...')
        time.sleep(1)
    return datetime.now()
