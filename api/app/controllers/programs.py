from flask import request, jsonify, Blueprint
from api.app.db.ies import DB
from app.schemas.program_schema import validate_post_schema, validate_put_schema
from flask_jwt_extended import jwt_required
from app.utils.utils import exception, _format, _format
# Relaciones
from app.controllers.faculties import exists as exists_faculty

Program = Blueprint('Program', __name__)
db = DB.getInstance()

table = 'VWPROGRAMADESERCION'


@Program.route('')
@Program.route('/')
@jwt_required()
def get():
    query = db.select('SELECT * FROM {};'.format(table))
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
        'SELECT * FROM {} WHERE codigo={};'.format(table, codigo))
    ex = exception(query)
    if ex:
        return ex
    if not (query):
        return {'msg': 'Not found'}, 404
    return jsonify(_format(query)[0])


@Program.route('faculty/<int:faculty>')
@jwt_required()
def getByFacultad(faculty):
    query = db.select(
        'SELECT * FROM {} WHERE faculty={};'.format(table, faculty))
    ex = exception(query)
    if ex:
        return ex
    if not (query):
        return {'msg': 'Not found'}, 404
    return jsonify(_format(query))


@Program.route('', methods=['POST'])
@jwt_required()
def post():
    body = request.get_json()
    # validate schema
    if not (validate_post_schema(body)):
        return {'error': 'invalid body content'}, 400
    # sql validations
    if not exists_faculty(body['faculty']):
        return {'error': 'faculty no existe'}, 404
    lista = db.select('SELECT * FROM {};'.format(table))
    for p in lista:
        if p['codigo'] == body['codigo']:
            return {'error': 'codigo ya existe'}, 400
        if p['name'] == body['name']:
            return {'error': 'name ya existe'}, 400
    # Insert
    insert = db.insert(body, '{}'.format(table))
    ex = exception(insert)
    if ex:
        return ex
    return {'msg': 'Program created'}, 200


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
        return {'error': 'invalid body content'}, 400
    # sql validations
    if not exists(codigo):
        return {'error': 'Program no existe'}, 404
    # Uptade
    condicion = 'codigo='+str(codigo)
    update = db.update(body, condicion, '{}'.format(table))
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
    delete = db.delete(condicion, '{}'.format(table))
    ex = exception(delete)
    if ex:
        return ex
    return {'msg': 'Program eliminado'}, 200


def exists(codigo):
    codigo = int(codigo)
    query = db.select('SELECT * FROM {};'.format(table))
    if exception(query):
        return False
    lista = map(lambda p: p['codigo'], query)
    return True if codigo in lista else False
