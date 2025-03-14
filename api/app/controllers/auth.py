from flask import request, jsonify, Blueprint
from flask_jwt_extended import create_access_token
import datetime as dt
from hashlib import md5

from app.schemas.auth_schema import validate_login_schema
from app.controllers.users import auth_login, create_user

Auth = Blueprint('auth', __name__)


@Auth.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({'msg': 'Request body is missing'}), 400

    if not validate_login_schema(request.json):
        return jsonify({'msg': 'Invalid body for login'}), 400

    email = request.json.get('email', None)
    password = request.json.get('password', '')
    clave_md5 = str(md5(password.encode()).hexdigest())

    user = auth_login(email, clave_md5)

    if not user:
        return jsonify({
            'msg': 'Incorrect email or password'
        }), 401

    access_token = create_access_token(
        identity=str(user),
        expires_delta=dt.timedelta(hours=3)
    )
    return jsonify(access_token=access_token), 200


@Auth.route('/singup', methods=['POST'])
def singup():
    body = request.get_json()
    return create_user(body)
