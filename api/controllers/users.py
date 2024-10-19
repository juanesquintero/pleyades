from flask import request, jsonify, Blueprint
from schemas.user_schema import validate_post_schema, validate_put_schema
from db.pleyades.db import User as user_model
from flask_jwt_extended import jwt_required
from hashlib import md5
from utils.utils import exception, _format

# Relaciones
from controllers.faculties import exists as exists_faculty
from controllers.programs import exists as exists_program

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


@User.route('/<correo>')
@jwt_required()
def get_one(correo):
    query = user_model.get_one(correo)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'msg': 'No hay concidencias'}, 404
    return jsonify(query)


@User.route('rol/<rol>')
@jwt_required()
def getByRol(rol):
    query = user_model.get_rol(rol)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'msg': 'No hay concidencias'}, 404
    return jsonify(query)


@User.route('', methods=['POST'])
@jwt_required()
def post():
    body = request.get_json()
    return create_user(body)


def create_user(body):
    # validate schema
    if not validate_post_schema(body):
        return {'error': 'body invalido'}, 400
    # sql validations
    if exists(body.get('correo')):
        return {'error': 'correo ya existe'}, 400
    if body.get('faculty'):
        if not exists_faculty(body['faculty']):
            return {'error': 'faculty no existe'}, 404
    if body.get('programa'):
        if not exists_program(body['programa']):
            return {'error': 'programa no existe'}, 404
    if not body['rol'] in ['Analista', 'Admin']:
        return {'error': 'Rol invalido'}, 404
    # Insert
    insert = user_model.insert(body)
    ex = exception(insert)
    if ex:
        return ex
    return {'msg': 'User creado'}, 200


@ User.route('/', methods=['POST'])
@ jwt_required()
def post2():
    return post()


@ User.route('/<correo>', methods=['PUT'])
@ jwt_required()
def put(correo):
    body = request.get_json()
    if not correo:
        return {'error': 'indique el correo por el path'}, 404
    # validate schema
    if not validate_put_schema(body):
        return {'error': 'body invalido'}, 400
    # sql validations
    if not exists(correo):
        return {'error': 'User no existe'}, 404
    if body.get('faculty'):
        if not exists_faculty(body['faculty']):
            return {'error': 'faculty no existe'}, 404
    if body.get('program'):
        if not exists_program(body['programa']):
            return {'error': 'programa no existe'}, 404
    if 'clave' in body.keys():
        body['clave'] = str(md5(body['clave'].encode()).hexdigest())

    # Uptade
    update = user_model.update(correo, body)
    ex = exception(update)
    if ex:
        return ex
    return {'msg': 'User actualizado'}, 200


@ User.route('/<correo>', methods=['DELETE'])
@ jwt_required()
def delete_one(correo):
    if not correo:
        return {'error': 'indique el correo por el path'}, 404
    # sql validations
    if not exists(correo):
        return {'error': 'User no existe'}, 404
    # delete
    delete = user_model.delete(correo)
    ex = exception(delete)
    if ex:
        return ex
    return {'msg': 'User eliminado'}, 200


def exists(correo):
    query = user_model.get_all()
    if exception(query):
        return False
    lista = map(lambda u: u['correo'], query)
    return True if correo in lista else False


def auth(correo, clave):
    query = user_model.get_login(correo, clave)

    if query:
        return True, query

    return False, None
