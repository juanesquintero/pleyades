import re
import os
import json
import logging
import pandas as pd
from flask import render_template
from datetime import datetime
from web.app.services.API import post, put, get

error_logger = logging.getLogger('error_logger')


def clean_exception(ex):
    ip_port = '[0-9]+(?:\.[0-9]+){3}(:[0-9]+)?'
    error = re.sub(ip_port, '', str(ex))

    words = ['MYSQL', 'SQL', 'MARIADB', 'MICROSOFT', 'SQL SERVER', 'ODBC']
    for word in words:
        error = re.sub(word+'(?i)', '', error)
    symbols = ['[', ']', '"', ')', '(']
    for symbol in symbols:
        error = error.replace(symbol, '')

    return error


def exception(op):
    if isinstance(op, Exception):
        ex = clean_exception(str(op))
        error_logger.error(ex)
        return render_template('utils/message.html', message='An error occurred accessing the data'), 500
    else:
        return False

####################################### Repetitive logical functions ###############################################


def get_now_date():
    format = '%Y-%m-%d %H:%M:%S'
    date = datetime.strftime(datetime.now(), format)
    # Format for the API and the database
    formatted_date = date.replace(' ', 'T')+'+00:00'
    return formatted_date


def set_date_format(results):
    for r in results:
        r['startDate'] = str_to_date(r['startDate'])
        r['endDate'] = str_to_date(r['endDate'])
    return results


def str_to_date(date):
    read_format = '%Y-%m-%d %H:%M:%S'
    write_format = '%A %d/%B/%Y - %H:%M %p'
    read_date = datetime.strptime(date, read_format)
    write_date = read_date.strftime(write_format)
    return write_date.title()


def save_file(data, path, type):
    try:
        if type == 'excel':
            data.to_excel(path, engine='openpyxl', index=False)
        elif type == 'json':
            data.to_json(path, orient='records')
        else:
            raise Exception(
                'Could not save the file \n Incorrect file type'
            )
    except Exception as e:
        error_logger.error(e)
        raise Exception('Could not save the file')
    return True, 'ERROR'


def remove_file(path):
    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception as e:
            error_logger.error(e)
            return False, render_template('utils/message.html', message='Could not delete the file')
    # else:
    #     return False, render_template('utils/message.html', message='Could not delete the file', submessage='The file does not exist')
    return True, 'ERROR'


def get_excel_file(path):
    if os.path.exists(path+'.xlsx'):
        data = pd.read_excel(path+'.xlsx')
    elif os.path.exists(path+'.xls'):
        data = pd.read_excel(path+'.xls')
    else:
        return False, render_template('utils/message.html', message='File not found')
    return True, data


def get_json_file(path):
    if os.path.exists(path+'.json'):
        try:
            with open(path+'.json', 'r') as json_file:
                data = json.load(json_file)
        except Exception as e:
            error_logger.error(e)
            return False, render_template('utils/message.html', message='Could not open the deserters file:')
    else:
        return False, render_template('utils/message.html', message='Deserters file not found')
    return True, data


def update_status(name, status):
    status, body = put('datasets/'+name, {'status': status})
    if not status:
        return render_template('utils/message.html', message='Could not update the dataset status to '+status, submessage=body)
    else:
        return None


def save_preparation(preparation, observations, status):
    # Save preparation record
    preparation['endDate'] = get_now_date()
    preparation['observations'] = observations
    preparation['status'] = status
    post('preparations', preparation)
    return True, 'ERROR'


def save_execution(execution, results, status):

    # Save execution record
    execution['model_accuracy'] = results.get('accuracy', None)
    execution['endDate'] = get_now_date()
    execution['results'] = dict(results)
    execution['status'] = status

    status, body = post('executions', dict(execution))

    if not status:
        raise Exception(
            f"Execution could NOT be saved: {body.get('error')}"
        )

    return True, 'ERROR'


def get_dataset_name(dataset):
    # Get dataset name from the API
    status_n, body_n = post('datasets/name', dataset)
    if status_n:
        return body_n['name'], body_n['number']

    error_logger.error(f'API ERROR: {status_n} {body_n}')
    return False, render_template('utils/message.html', message='Could not get the dataset name', submessage=body_n)


def get_execution_name(dataset):
    # Get execution name from the API
    status_n, body_n = get(f'executions/name/{dataset}')
    if status_n:
        return body_n['name'], body_n['number']

    error_logger.error(f'API ERROR: {status_n} {body_n}')
    raise Exception('Could not get the execution name')


def get_ies_config():
    # Get IES definition
    ies_name = os.getenv('CLI_IES_NAME')
    base_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f'{base_dir}/../../ies.json', 'r') as json_file:
        try:
            IES = json.load(json_file).get(ies_name)
            return IES
        except Exception as e:
            error_logger.error('EXCEPTION: IES Config ERROR: {}'.format(e))
            return {
                'name': 'Educatic',
                'url': 'http://educatic.com.co/',
                'logo': 'http://educatic.com.co/assets/images/logo.png',
                'description': 'Office: Carrera 42 No 5 SUR 145 Piso 13, office 125 WeWork, Medellín, Antioquia Mobile: (+57) 311 634 45 26 Email: walter.alvarez@educatic.com.co Service and Support: soporte@educatic.com.co (+57) 311 634 45 26'
            }
