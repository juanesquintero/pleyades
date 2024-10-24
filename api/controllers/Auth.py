from flask import request, jsonify, Blueprint
from flask_jwt_extended import (create_access_token)
import datetime as dt
from hashlib import md5

from schemas.auth_schema import validate_login_schema
from controllers.users import auth, create_user

Auth = Blueprint('auth', __name__)


@Auth.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({'msg': 'Falta body en el request'}), 400

    if not validate_login_schema(request.json):
        return jsonify({'msg': 'Body invalido para login'}), 400

    correo = request.json.get('correo', None)
    clave = request.json.get('clave', '')
    clave_md5 = str(md5(clave.encode()).hexdigest())

    user = auth(correo, clave_md5)

    if user == (False, None):
        return jsonify({'msg': 'Correo o clave incorrectos'}), 401

    if user[0] is True:
        access_token = create_access_token(
            identity=user[1], expires_delta=dt.timedelta(hours=3)
        )
        return jsonify(access_token=access_token), 200

    return user[1]


@Auth.route('/singup', methods=['POST'])
def singup():
    body = request.get_json()
    return create_user(body)
