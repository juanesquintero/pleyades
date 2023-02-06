import os
import dotenv
import requests
from flask import session

dotenv.load_dotenv()

api_path = 'http://api-host/' + os.getenv('CLI_IES_NAME') + '/'

def get(endpoint):
    res = requests.get(api_path+endpoint, headers=session.get('headers'))
    status, body = res.status_code, res.json()
    if (status == 200):
        return True, body
    else:
        return False, body


def post(endpoint, body_json):
    res = requests.post(
        api_path+endpoint,
        json=body_json,
        headers=session.get('headers')
    )
    status, body = res.status_code, res.json()
    if (status == 200):
        return True, body
    else:
        return False, body


def put(endpoint, body_json):
    res = requests.put(
        api_path+endpoint,
        json=body_json,
        headers=session.get('headers')
    )
    status, body = res.status_code, res.json()
    if (status == 200):
        return True, body
    else:
        return False, body


def delete(endpoint):
    res = requests.delete(api_path+endpoint, headers=session.get('headers'))
    status, body = res.status_code, res.json()
    if (status == 200):
        return True, body
    else:
        return False, body
