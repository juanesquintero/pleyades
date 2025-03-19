from flask import request, jsonify, Blueprint
from app.schemas.user_schema import validate_post_schema, validate_put_schema
from api.app.db.pleyades import User as user_model
from flask_jwt_extended import jwt_required
from hashlib import md5
from app.utils.utils import exception, _format

# Relaciones
from app.controllers.faculties import exists as exists_faculty
from app.controllers.programs import exists as exists_program

User = Blueprint('User', __name__)


@User.route('')
@User.route('/')
@jwt_required()
def get():
    query = user_model.get_all()
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'msg': 'No hay Usuarios'}, 404
    return jsonify(query)


@User.route('/<email>')
@jwt_required()
def get_one(email):
    query = user_model.get_one(email)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'msg': 'Not found'}, 404
    return jsonify(query)


@User.route('role/<role>')
@jwt_required()
def getByRol(role):
    query = user_model.get_rol(role)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'msg': 'Not found'}, 404
    return jsonify(query)


@User.route('', methods=['POST'])
@jwt_required()
def post():
    body = request.get_json()
    return create_user(body)


def create_user(body):
    # validate schema
    if not validate_post_schema(body):
        return {'error': 'invalid body content'}, 400
    # sql validations
    if exists(body.get('email')):
        return {'error': 'email ya existe'}, 400
    if body.get('faculty'):
        if not exists_faculty(body['faculty']):
            return {'error': 'faculty no existe'}, 404
    if body.get('program'):
        if not exists_program(body['program']):
            return {'error': 'program no existe'}, 404
    if not body['role'] in ['Analyst', 'Admin']:
        return {'error': 'Rol invalido'}, 404
    # Insert
    insert = user_model.insert(body)
    ex = exception(insert)
    if ex:
        return ex
    return {'msg': 'User created'}, 200


@User.route('/', methods=['POST'])
@jwt_required()
def post2():
    return post()


@User.route('/<email>', methods=['PUT'])
@jwt_required()
def put(email):
    body = request.get_json()
    if not email:
        return {'error': 'indique el email por el path'}, 404
    # validate schema
    if not validate_put_schema(body):
        return {'error': 'invalid body content'}, 400
    # sql validations
    if not exists(email):
        return {'error': 'User no existe'}, 404
    if body.get('faculty'):
        if not exists_faculty(body['faculty']):
            return {'error': 'faculty no existe'}, 404
    if body.get('program'):
        if not exists_program(body['program']):
            return {'error': 'program no existe'}, 404
    if 'password' in body.keys():
        body['password'] = str(md5(body['password'].encode()).hexdigest())

    # Uptade
    update = user_model.update(email, body)
    ex = exception(update)
    if ex:
        return ex
    return {'msg': 'User actualizado'}, 200


@User.route('/<email>', methods=['DELETE'])
@jwt_required()
def delete_one(email):
    if not email:
        return {'error': 'indique el email por el path'}, 404
    # sql validations
    if not exists(email):
        return {'error': 'User no existe'}, 404
    # delete
    delete = user_model.delete(email)
    ex = exception(delete)
    if ex:
        return ex
    return {'msg': 'User eliminado'}, 200


def exists(email):
    query = user_model.get_all()
    if exception(query):
        return False
    user_list = map(lambda user: user.get('email'), query)
    return bool(email in user_list)


def auth_login(email, password):
    return user_model.get_login(
        email,
        password
    )
