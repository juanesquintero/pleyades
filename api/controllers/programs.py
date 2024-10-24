from flask import request, jsonify, Blueprint
from db.ies.db import DB
from schemas.program_schema import validate_post_schema, validate_put_schema
from flask_jwt_extended import jwt_required
from utils.utils import exception, _format, _format
# Relaciones
from controllers.faculties import exists as exists_faculty

Program = Blueprint('Program', __name__)
db = DB.getInstance()

tabla = 'VWPROGRAMADESERCION'


@Program.route('')
@Program.route('/')
@jwt_required()
def get():
    query = db.select('SELECT * FROM {};'.format(tabla))
    ex = exception(query)
    if ex:
        return ex
    if not (query):
        return {'msg': 'No hay programs'}, 404
    return jsonify(_format(query))


@Program.route('/<int:codigo>')
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


@Program.route('faculty/<int:faculty>')
@jwt_required()
def getByFacultad(faculty):
    query = db.select(
        'SELECT * FROM {} WHERE faculty={};'.format(tabla, faculty))
    ex = exception(query)
    if ex:
        return ex
    if not (query):
        return {'msg': 'No hay concidencias'}, 404
    return jsonify(_format(query))


@Program.route('', methods=['POST'])
@jwt_required()
def post():
    body = request.get_json()
    # validate schema
    if not (validate_post_schema(body)):
        return {'error': 'body invalido'}, 400
    # sql validations
    if not exists_faculty(body['faculty']):
        return {'error': 'faculty no existe'}, 404
    lista = db.select('SELECT * FROM {};'.format(tabla))
    for p in lista:
        if p['codigo'] == body['codigo']:
            return {'error': 'codigo ya existe'}, 400
        if p['nombre'] == body['nombre']:
            return {'error': 'nombre ya existe'}, 400
    # Insert
    insert = db.insert(body, '{}'.format(tabla))
    ex = exception(insert)
    if ex:
        return ex
    return {'msg': 'Program creado'}, 200


@Program.route('/', methods=['POST'])
@jwt_required()
def post2():
    return post()


@Program.route('/<int:codigo>', methods=['PUT'])
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
        return {'error': 'Program no existe'}, 404
    # Uptade
    condicion = 'codigo='+str(codigo)
    update = db.update(body, condicion, '{}'.format(tabla))
    ex = exception(update)
    if ex:
        return ex
    return {'msg': 'Program actualizado'}, 200


@Program.route('/<int:codigo>', methods=['DELETE'])
@jwt_required()
def delete_one(codigo):
    if not (codigo):
        return {'error': 'indique el codigo por el path'}, 404
    # sql validations
    if not exists(codigo):
        return {'error': 'Program no existe'}, 404
    # delete
    condicion = 'codigo='+str(codigo)
    delete = db.delete(condicion, '{}'.format(tabla))
    ex = exception(delete)
    if ex:
        return ex
    return {'msg': 'Program eliminado'}, 200


def exists(codigo):
    codigo = int(codigo)
    query = db.select('SELECT * FROM {};'.format(tabla))
    if exception(query):
        return False
    lista = map(lambda p: p['codigo'], query)
    return True if codigo in lista else False
