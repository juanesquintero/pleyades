from flask import request, jsonify, Blueprint
from schemas.usuario_schema import validate_post_schema, validate_put_schema
from db.pleyades.db import User as usuario_model
from flask_jwt_extended import jwt_required
from hashlib import md5
from utils.utils import exception, _format

# Relaciones
from controllers.Facultades import exists as exists_facultad
from controllers.Programas import exists as exists_programa

User = Blueprint('User', __name__)


@User.route('')
@User.route('/')
@jwt_required()
def get():
    query = usuario_model.get_all()
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'msg': 'No hay Usuarios'}, 404
    return jsonify(query)


@User.route('/<correo>')
@jwt_required()
def get_one(correo):
    query = usuario_model.get_one(correo)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'msg': 'No hay concidencias'}, 404
    return jsonify(query)


@User.route('rol/<rol>')
@jwt_required()
def getByRol(rol):
    query = usuario_model.get_rol(rol)
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
    if exists(body['correo']):
        return {'error': 'correo ya existe'}, 400
    if 'facultad' in body.keys() and body['facultad'] is not None:
        if not exists_facultad(body['facultad']):
            return {'error': 'facultad no existe'}, 404
    if 'programa' in body.keys() and body['programa'] is not None:
        if not exists_programa(body['programa']):
            return {'error': 'programa no existe'}, 404
    if not body['rol'] in ['Analista', 'Admin']:
        return {'error': 'Rol invalido'}, 404
    # Insert
    insert = usuario_model.insert(body)
    ex = exception(insert)
    if ex:
        return ex
    return {'msg': 'User creado'}, 200


@User.route('/', methods=['POST'])
@jwt_required()
def post2():
    return post()


@User.route('/<correo>', methods=['PUT'])
@jwt_required()
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
    if ('facultad' in body.keys() and body['facultad'] != None):
        if not exists_facultad(body['facultad']):
            return {'error': 'facultad no existe'}, 404
    if ('programa' in body.keys() and body['programa'] != None):
        if not exists_programa(body['programa']):
            return {'error': 'programa no existe'}, 404
    if 'clave' in body.keys():
        body['clave'] = str(md5(body['clave'].encode()).hexdigest())

    # Uptade
    update = usuario_model.update(correo, body)
    ex = exception(update)
    if ex:
        return ex
    return {'msg': 'User actualizado'}, 200


@User.route('/<correo>', methods=['DELETE'])
@jwt_required()
def delete_one(correo):
    if not correo:
        return {'error': 'indique el correo por el path'}, 404
    # sql validations
    if not exists(correo):
        return {'error': 'User no existe'}, 404
    # delete
    delete = usuario_model.delete(correo)
    ex = exception(delete)
    if ex:
        return ex
    return {'msg': 'User eliminado'}, 200


def exists(correo):
    query = usuario_model.get_all()
    if exception(query):
        return False
    lista = map(lambda u: u['correo'], query)
    return True if correo in lista else False


def auth(correo, clave):
    query = usuario_model.get_login(correo, clave)

    if query:
        return True, query

    return False, None
