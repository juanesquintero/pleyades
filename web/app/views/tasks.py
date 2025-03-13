import traceback
from web.app.utils.tasks import sleep_task
from celery.result import AsyncResult
from flask import Blueprint


Tasks = Blueprint('Tasks', __name__)


@Tasks.route('/test/sleep/')
@Tasks.route('/test/sleep/<int:seconds>')
def set_schedule_task(seconds: int = 15):
    try:
        result = sleep_task.delay(seconds)
    except Exception as e:
        error = str(e) + '\n' + traceback.format_exc()
        return {"error": error}
    return {"result_id": result.id}


@Tasks.route('/test/result/<id>')
def get_task_result(id: str) -> dict[str, object]:
    result = AsyncResult(id)
    return {
        "ready": result.ready(),
        "successful": result.successful(),
        "value": result.result if result.ready() else None,
    }
