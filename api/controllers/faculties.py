from utils.utils import exception, _format
from db.ies.db import DB
from flask_jwt_extended import jwt_required
from flask import request, jsonify, Blueprint
from schemas.facultad_schema import validate_post_schema, validate_put_schema


Faculty = Blueprint('facultad', __name__)

tabla = 'VWFACULTADDESERCION'

db = DB.getInstance()


@Faculty.route('')
@Faculty.route('/')
@jwt_required()
def get():
    query = db.select('SELECT * FROM {};'.format(tabla))
    ex = exception(query)
    if ex:
        return ex
    if not (query):
        return {'msg': 'No hay Facultades'}, 404
    return jsonify(_format(query))


@Faculty.route('/<codigo>')
@jwt_required()
def get_one(codigo):
    query = db.select(
        'SELECT * FROM {} WHERE codigo={};'.format(tabla, codigo))
    ex = exception(query)
    if ex:
        return ex
    if not (query):
        return {'msg': 'No hay concidencias'}, 404
    return jsonify(_format(query)[0])


@Faculty.route('', methods=['POST'])
@jwt_required()
def post():
    body = request.get_json()
    # validate schema
    if not (validate_post_schema(body)):
        return {'error': 'body invalido'}, 400
    # sql validations
    lista = db.select('SELECT * FROM {};'.format(tabla))
    for f in lista:
        if f['codigo'] == body['codigo']:
            return {'error': 'codigo ya existe'}, 400
        if f['nombre'] == body['nombre']:
            return {'error': 'nombre ya existe'}, 400
    # Insert
    insert = db.insert(body, '{}'.format(tabla))
    ex = exception(insert)
    if ex:
        return ex
    return {'msg': 'facultad creada'}, 200


@Faculty.route('/', methods=['POST'])
@jwt_required()
def post2():
    return post()


@Faculty.route('/<codigo>', methods=['PUT'])
@jwt_required()
def put(codigo):
    body = request.get_json()
    if not (codigo):
        return {'error': 'indique el codigo por el path'}, 404
    # validate schema
    if not (validate_put_schema(body)):
        return {'error': 'body invalido'}, 400
    # sql validations
    if not exists(codigo):
        return {'error': 'facultad no existe'}, 404
    # Uptade
    condicion = 'codigo='+str(codigo)
    update = db.update(body, condicion, '{}'.format(tabla))
    ex = exception(update)
    if ex:
        return ex
    return {'msg': 'facultad actualizada'}, 200


@Faculty.route('/<codigo>', methods=['DELETE'])
@jwt_required()
def delete_one(codigo):
    if not (codigo):
        return {'error': 'indique el codigo por el path'}, 404
    # sql validations
    if not exists(codigo):
        return {'error': 'facultad no existe'}, 404
    # delete
    condicion = 'codigo='+str(codigo)
    delete = db.delete(condicion, '{}'.format(tabla))
    ex = exception(delete)
    if ex:
        return ex
    return {'msg': 'facultad eliminada'}, 200


def exists(codigo):
    codigo = int(codigo)
    query = db.select('SELECT * FROM {};'.format(tabla))
    if exception(query):
        return False
    lista = map(lambda f: f['codigo'], query)
    return True if codigo in lista else False
