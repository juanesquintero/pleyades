import dotenv
import logging
import requests
from flask import session

dotenv.load_dotenv()

api_path = 'http://api/'
# api_path = 'http://api/' + os.getenv('CLI_IES_NAME') + '/'
error_logger = logging.getLogger('error_logger')


def get(endpoint):
    res = requests.get(api_path+endpoint, headers=session.get('headers'))
    status, body = res.status_code, res.json()
    return result(endpoint, status, body)


def post(endpoint, body_json):
    res = requests.post(
        api_path+endpoint,
        json=body_json,
        headers=session.get('headers')
    )
    status, body = res.status_code, res.json()
    return result(endpoint, status, body)


def put(endpoint, body_json):
    res = requests.put(
        api_path+endpoint,
        json=body_json,
        headers=session.get('headers')
    )
    status, body = res.status_code, res.json()
    return result(endpoint, status, body)


def delete(endpoint):
    res = requests.delete(api_path+endpoint, headers=session.get('headers'))
    status, body = res.status_code, res.json()
    return result(endpoint, status, body)

def status_group(status):
    return int(str(status)[0])


def result(endpoint, status, body):
    if status_group(status) == 2:
        return True, body
    
    msg = body.get('msg')
    if msg:
        if 'sesión' in msg  or 'expirado' in msg:
            raise Exception(body.get('msg'))

        if '/desercion/' in endpoint:
            if msg == 'No hay concidencias' or status == 404:
                raise Exception('No se encontraron concidencias, por favor revise la base de datos', status=404)

    error_logger.error(f'\nAPI ERROR...{endpoint} - {status}: {body}\n')
    return False, body
