import os, dotenv, requests
from flask import session

dotenv.load_dotenv()

api = os.getenv("API_PATH")

def get(endpoint):
    res = requests.get(api+endpoint,headers=session['headers'])
    status, body = res.status_code, res.json()
    if (status == 200):
        return True, body
    else:
        return False, body

def post(endpoint,body_json):
    res = requests.post(api+endpoint, json=body_json,headers=session['headers'])
    status, body = res.status_code, res.json()
    if (status == 200):
        return True, body
    else:
        return False, body

def put(endpoint,body_json):
    res = requests.put(api+endpoint, json=body_json,headers=session['headers'])
    status, body = res.status_code, res.json()
    if (status == 200):
        return True, body
    else:
        return False, body

def delete(endpoint):
    res = requests.delete(api+endpoint,headers=session['headers'])
    status, body = res.status_code, res.json()
    if (status == 200):
        return True, body
    else:
        return False, body