from web.app.utils.tasks import run_task, sleep_task, schedule_preparation_task
from celery.result import AsyncResult
from flask import Blueprint


Tasks = Blueprint('Tasks', __name__)


@Tasks.route('/test/sleep/')
@Tasks.route('/test/sleep/<int:seconds>')
def set_schedule_test_task(seconds: int = 15):
    result = run_task(sleep_task, seconds=seconds)
    return {"result": result}


@Tasks.route('/test/result/<id>')
def get_test_task_result(id: str) -> dict[str, object]:
    result = AsyncResult(id)
    return {
        "ready": result.ready(),
        "successful": result.successful(),
        "value": result.result if result.ready() else None,
    }
