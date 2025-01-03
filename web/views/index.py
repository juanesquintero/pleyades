import traceback
from flask import render_template, session, Blueprint
from tasks.test import sleep_task
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


@Index.route('/task/schedule/')
@Index.route('/task/schedule/<int:seconds>')
def set_schedule_task(seconds: int = 5):
    try:
        result = sleep_task.delay(seconds)
    except Exception as e:
        error = str(e) + '\n' + traceback.format_exc()
        return {"error": error}
    return {"result_id": result.id}


@Index.route('/task/result/<int:id>')
def get_task_result(id: int) -> dict[str, object]:
    result = AsyncResult(id)
    return {
        "ready": result.ready(),
        "successful": result.successful(),
        "value": result.result if result.ready() else None,
    }
