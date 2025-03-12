import traceback
from flask import render_template, session, Blueprint
from web.app.tasks.test import sleep_task
from celery.result import AsyncResult


Index = Blueprint('Index', __name__)


@Index.route('/')
@Index.route('/home')
def home():
    return render_template('utils/home.html'), 200


@Index.route('/contact')
def contact():
    ies = session.get('ies', {})
    return render_template('utils/contact.html', ies=ies), 200


@Index.route('/_/tasks/schedule/')
@Index.route('/_/tasks/schedule/<int:seconds>')
def set_schedule_task(seconds: int = 15):
    try:
        result = sleep_task.delay(seconds)
    except Exception as e:
        error = str(e) + '\n' + traceback.format_exc()
        return {"error": error}
    return {"result_id": result.id}


@Index.route('/_/tasks/result/<id>')
def get_task_result(id: str) -> dict[str, object]:
    result = AsyncResult(id)
    return {
        "ready": result.ready(),
        "successful": result.successful(),
        "value": result.result if result.ready() else None,
    }
