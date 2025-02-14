import os
import json
import logging
import pandas as pd
from ast import literal_eval
from dotenv import load_dotenv
from flask import request, session, Blueprint, render_template, send_file, redirect, url_for, jsonify, flash

import web.utils.model as Model
from web.services.API import get, post
import web.views.datasets as datasets
from web.views.auth import login_required
import web.utils.dashboards.data_ies as DataIES
from web.utils.mixins import save_file, save_execution, get_now_date, get_execution_name

load_dotenv()

error_logger = logging.getLogger('error_logger')

endpoint = 'analist/models/'

Analyst = Blueprint('Analyst', __name__)

upload_folder = os.getcwd()+'/uploads'
models_folder = f'{upload_folder}/models'


@Analyst.route('/models', methods=['GET'])
@Analyst.route('/models/', methods=['GET'])
@login_required
def models():
    model = request.args.get('model')
    success, body = get_models(model)

    if not success:
        flash('User does not have desertion models', 'warning')
        body = []

    return render_template(
        'analist/models/list.html',
        models=body,
    )


@Analyst.route('/models/train', methods=['GET', 'POST'])
@login_required
def train():
    if request.method == 'GET':
        return form_train()
    dataset = dict(request.values)
    return datasets.post_save(dataset)


@Analyst.route('/models/predict', methods=['POST'])
def predict():
    model = dict(request.values).get('model')
    return render_template(
        endpoint+'predict.html',
        model=literal_eval(model)
    )


@Analyst.route('/trainings', methods=['GET'])
@Analyst.route('/trainings/', methods=['GET'])
@login_required
def trainings():
    model = request.args.get('model')
    success, body = get_models(model)

    if not success:
        flash('User does not have trainings', 'info')
        body = []

    return render_template(
        'analist/trainings.html',
        trainings=body,
    )


@Analyst.route('/predictions', methods=['GET'])
@Analyst.route('/predictions/', methods=['GET'])
@login_required
def predictions():
    model = request.args.get('model')
    success, body = get_models(model)

    if not success:
        flash('User does not have predictions', 'info')
        body = []

    return render_template(
        'analist/predictions.html',
        predictions=body,
    )


@Analyst.route('/predictions/predict', methods=['POST'])
def predict_model():
    form = dict(request.values)
    execution = literal_eval(form.get('execution'))
    execution['startDate'] = get_now_date()

    period = form.get('period')
    results = execution.pop('results')
    model = execution.get('dataset')
    program_id = results.get('program_id')

    basic_info = {
        'program_id': program_id,
        'program': results.get('program'),
        'faculty_id': results.get('faculty_id'),
        'faculty': results.get('faculty'),
        'model': model
    }

    # Get students to predict
    data_to_predict = DataIES.get_students_period_program(
        period, program_id
    )

    # Prepare data
    df_data_to_predict = pd.DataFrame(data_to_predict)
    prepared_data = Model.prepare_data(df_data_to_predict)

    # Predict results
    model_results, desertion_results = Model.predict(
        prepared_data, period, basic_info
    )
    desertion_results['program_id'] = desertion_results['program_id'].astype(
        int
    )
    desertion_results['prediction_semester'] = desertion_results['prediction_semester'].astype(
        int
    )

    # Insert results
    if desertion_results.empty:
        flash('No desertions for this prediction', 'warning')
        return redirect(url_for('Analyst.models'))

    results_insert = json.loads(
        desertion_results.to_json(orient='records')
    )

    status_insert, body_insert = post(
        'desertion/results',
        results_insert
    )

    if not status_insert:
        error_logger.error(
            'Error inserting new desertions'.format(
                json.dumps(body_insert))
        )
        raise Exception(
            'An error occurred inserting and/or updating the results'
        )

    execution['name'], execution['number'] = get_execution_name(model)

    # Save desertions
    desertion_file = f"D {execution.get('name')}.json"
    path = upload_folder+'/deserters/'+desertion_file
    save_file(
        model_results.pop('desertions'), path, 'json'
    )

    # Save execution
    model_results['duration'] = execution.pop('duration')
    save_execution(execution, model_results, 'Successful')
    flash('Prediction successful!!', 'success')

    return redirect(url_for('Analyst.predictions'))


@Analyst.route('/models/download', methods=['POST'])
@login_required
def download():
    model = dict(request.values).get('model')
    path = f'{models_folder}/{model}.pkl'

    if os.path.exists(path):
        return send_file(path, as_attachment=True)

    success, body = get_models()

    flash('File not found for download', 'warning')

    if not success:
        flash(f"{body.get('error')}", 'danger')

    return render_template(
        'analist/models/list.html',
        models=body,
    )


@Analyst.route('/models/periods/<int:program>')
@login_required
def get_periods_program(program):
    status, body = get(f'desertion/students/periods/program/{program}')
    if status:
        return jsonify(body)
    return jsonify([])


def get_models(name=None, dataset=None):
    user = session.get('user', {'email': ''}).get('email')
    endpoint = f'executions/executor/{user}'
    if name:
        endpoint += f'?name={name}'
    elif dataset:
        endpoint += f'?dataset={dataset}'
    return get(endpoint)


def form_train():
    periods = DataIES.get_periods_origin()
    status_f, body_f = get('faculties')
    status_p, body_p = get('programs')

    if status_f and status_p and periods:
        return render_template(endpoint+'create.html', faculties=body_f, programs=body_p)

    if not status_f and not status_p:
        error = {**body_f, **body_p}
    elif not status_f:
        error = body_f
    else:
        error = body_p
    return render_template(
        'utils/message.html',
        message='Could not load programs and faculties',
        submessage=error
    )
