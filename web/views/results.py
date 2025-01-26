import os
import pandas as pd
from dotenv import load_dotenv
from flask import request, session, Blueprint, render_template, send_file
from views.auth import login_required
from services.API import get
from utils.mixins import save_file, get_json_file, set_date_format

load_dotenv()

endpoint = 'results/'

Result = Blueprint('Result', __name__)

upload_folder = os.getcwd()+'/uploads'


@Result.route('/preparations')
@Result.route('/preparations/<dataset>')
@login_required
def preparations(dataset=None):
    if dataset:
        return list_set('preparations', dataset)
    return get_list('preparations')


@Result.route('/executions')
@Result.route('/executions/<dataset>')
@login_required
def executions(dataset=None):
    if dataset:
        return list_set('executions', dataset)
    return get_list('executions')


def get_list(results):
    role = 'preparer' if results == 'preparations' else 'executor'
    status, body = get(results+'/'+role+'/'+session.get('user')['email'])
    if status:
        return render_template(endpoint+results+'.html', results=set_date_format(body))
    else:
        return render_template(endpoint+results+'.html', results=[], error=body)


def list_set(results, dataset):
    status, body = get(results+'/dataset/'+dataset)
    if status:
        return render_template(endpoint+results+'.html', results=set_date_format(body))
    else:
        return render_template(endpoint+results+'.html', results=[], error=body)


@Result.route('/execution/detail', methods=['POST'])
@login_required
def execution_detail():
    body = dict(request.values)
    execution = body['execution']

    # Get the deserters file
    file = 'D '+execution
    path = upload_folder+'/deserters/'+file
    success, deserters = get_json_file(path)

    status, body = get('executions/'+execution)

    if status and success:
        del body['model_accuracy']
        del body['number']
        return render_template(endpoint+'execution_detail.html', deserters=deserters, results=body.pop('results'), execution=body)
    elif status and not success:
        if body['status'] == 'Failed':
            del body['model_accuracy']
            del body['number']
            return render_template(
                endpoint+'execution_detail.html',
                deserters=None,
                results=body.pop('results'),
                execution=body
            )
        else:
            return deserters
    else:
        return render_template(
            'utils/message.html',
            message='Could not get the execution',
            submessage=body
        )


@Result.route('/preparation/detail', methods=['POST'])
@login_required
def preparation_detail():
    body = dict(request.values)
    preparation = body['preparation']
    status, body = get('preparations/'+preparation)

    if status:
        del body['number']
        return render_template(
            endpoint+'preparation_detail.html',
            observations=body.pop('observations'),
            p=body
        )
    else:
        return render_template(
            'utils/message.html',
            message='Could not get the preparation results',
            submessage=body
        )


@Result.route('/download/deserters/<execution>', methods=['GET'])
@login_required
def download(execution):
    status_c, body_c = get('executions/'+execution)
    if not status_c:
        return render_template('utils/message.html', message='Execution does not exist')

    file = 'D '+execution
    path = upload_folder+'/deserters/'+file
    try:
        data = pd.read_json(path+'.json')
    except Exception as e:
        return render_template(
            'utils/message.html',
            message='Could not open the deserters file:',
            submessage=str(e)
        )

    success, error_page = save_file(data, path+'.xls', 'excel')
    if not success:
        return error_page

    return send_file(path+'.xls', as_attachment=True)
