from flask import request, jsonify, Blueprint
from db.ies.db_ies import DB
from schemas.programaSchema import validate_post_schema, validate_put_schema
from flask_jwt_extended import jwt_required
from utils.utils import exception, _format, _format
# Relaciones
from controllers.Facultades import exists as exists_facultad

Programa = Blueprint('Programa', __name__)
db = DB.getInstance()

tabla = 'VWPROGRAMADESERCION'

@Programa.route('')
@Programa.route('/')
@jwt_required()
def get():
    query = db.select('SELECT * FROM {};'.format(tabla))
    ex = exception(query)
    if ex:
        return ex
    if not(query):
        return {'msg': 'No hay programas'}, 404
    return jsonify(_format(query))


@Programa.route('/<int:codigo>')
@jwt_required()
def get_one(codigo):
    query = db.select(
        'SELECT * FROM {} WHERE codigo={};'.format(tabla, codigo))
    ex = exception(query)
    if ex:
        return ex
    if not(query):
        return {'msg': 'No hay concidencias'}, 404
    return jsonify(_format(query)[0])


@Programa.route('facultad/<int:facultad>')
@jwt_required()
def getByFacultad(facultad):
    query = db.select(
        'SELECT * FROM {} WHERE facultad={};'.format(tabla, facultad))
    ex = exception(query)
    if ex:
        return ex
    if not(query):
        return {'msg': 'No hay concidencias'}, 404
    return jsonify(_format(query))


@Programa.route('', methods=['POST'])
@jwt_required()
def post():
    body = request.get_json()
    # validate schema
    if not(validate_post_schema(body)):
        return {'error': 'body invalido'}, 400
    # sql validations
    if not exists_facultad(body['facultad']):
        return {'error': 'facultad no existe'}, 404
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
    return {'msg': 'Programa creado'}, 200


@Programa.route('/', methods=['POST'])
@jwt_required()
def post2():
    return post()


@Programa.route('/<int:codigo>', methods=['PUT'])
@jwt_required()
def put(codigo):
    body = request.get_json()
    if not(codigo):
        return {'error': 'indique el codigo por el path'}, 404
    # validate schema
    if not(validate_put_schema(body)):
        return {'error': 'body invalido'}, 400
    # sql validations
    if not exists(codigo):
        return {'error': 'Programa no existe'}, 404
    # Uptade
    condicion = 'codigo='+str(codigo)
    update = db.update(body, condicion, '{}'.format(tabla))
    ex = exception(update)
    if ex:
        return ex
    return {'msg': 'Programa actualizado'}, 200


@Programa.route('/<int:codigo>', methods=['DELETE'])
@jwt_required()
def delete_one(codigo):
    if not(codigo):
        return {'error': 'indique el codigo por el path'}, 404
    # sql validations
    if not exists(codigo):
        return {'error': 'Programa no existe'}, 404
    # delete
    condicion = 'codigo='+str(codigo)
    delete = db.delete(condicion, '{}'.format(tabla))
    ex = exception(delete)
    if ex:
        return ex
    return {'msg': 'Programa eliminado'}, 200


def exists(codigo):
    codigo = int(codigo)
    query = db.select('SELECT * FROM {};'.format(tabla))
    if exception(query):
        return False
    lista = map(lambda p: p['codigo'], query)
    return True if codigo in lista else False
