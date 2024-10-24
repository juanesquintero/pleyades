from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required
import json
from schemas.preparation_schema import validate_post_schema, validate_put_schema
from db.pleyades.db import Preparacion as preparation_model
from utils.utils import exception, _format
# Relaciones
from controllers.sets import exists as exists_set
from controllers.users import exists as exists_usuario

Preparacion = Blueprint('Preparacion', __name__)


@Preparacion.route('')
@Preparacion.route('/')
@jwt_required()
def get():
    query = preparation_model.get_all()
    ex = exception(query)
    if ex:
        return ex
    if not (query):
        return {'msg': 'No hay preparations'}, 404
    query = strdate_to_datetime(query)
    return jsonify(query)


@Preparacion.route('/<nombre>')
@jwt_required()
def get_one(nombre):
    query = preparation_model.get_one(nombre)
    ex = exception(query)
    if ex:
        return ex
    if not (query):
        return {'msg': 'No existe la preparación'}, 404
    query = strdate_to_datetime([query])
    return jsonify(query[0])


@Preparacion.route('/set/<set>')
@jwt_required()
def get_by_set(set):
    if not exists_set(set):
        return {'error': 'set no existe'}, 400
    query = preparation_model.get_set(set)
    ex = exception(query)
    if ex:
        return ex
    if not (query):
        return {'msg': 'Set no tiene preparations'}, 404
    query = strdate_to_datetime(query)
    return jsonify(query)


@Preparacion.route('/preparador/<preparador>')
@jwt_required()
def get_by_usuario(preparador):
    if not exists_usuario(preparador):
        return {'error': 'usuario no existe'}, 400
    query = preparation_model.get_preparador(preparador)
    ex = exception(query)
    if ex:
        return ex
    if not (query):
        return {'error': 'User no tiene preparations'}, 400
    query = strdate_to_datetime(query)
    return jsonify(query)


@Preparacion.route('/nombre/<set>')
@jwt_required()
def nombre(set):
    if not exists_set(set):
        return {'error': 'set no existe'}, 400
    # Obtener el numero consecutivo para el student_set de datos
    query = preparation_model.get_consecutivo(set)
    ex = exception(query)
    if ex:
        return ex
    if query:
        numero = query[0].get('numero')+1
    else:
        numero = 1
    return {'nombre': set+'.'+str(numero), 'numero': numero}, 200


@Preparacion.route('', methods=['POST'])
@jwt_required()
def post():
    body = request.get_json()
    # validate schema
    if not (validate_post_schema(body)):
        return {'error': 'body invalido'}, 400
    # sql validations
    if not exists_usuario(body['preparador']):
        return {'error': 'usuario no existe'}, 400
    if not exists_set(body['set']):
        return {'error': 'set no existe'}, 400
    if exists(body['nombre']):
        return {'error': 'preparation ya existe'}, 400
    # Cambiar formato de fechas
    body['fechaInicial'] = body['fechaInicial'].split('+')[0]
    body['fechaFinal'] = body['fechaFinal'].split('+')[0]
    # Cambiar formato de campo observaciones desde dict a str json para mysql
    body['observaciones'] = str(json.dumps(body['observaciones']))
    # Insert
    insert = preparation_model.insert(body)
    ex = exception(insert)
    if ex:
        return ex
    return {'msg': 'Preparacion creada'}, 200


@Preparacion.route('/', methods=['POST'])
@jwt_required()
def post2():
    return post()


@Preparacion.route('/<nombre>', methods=['PUT'])
@jwt_required()
def put(nombre):
    body = request.get_json()

    if not (nombre):
        return {'error': 'indique el nombre por el path'}, 400
    # validate schema
    if not (validate_put_schema(body)):
        return {'error': 'body invalido'}, 400
    # sql validations
    if not exists(nombre):
        return {'error': 'Preparacion no existe'}, 400
    # Cambiar formato de campo observaciones desde dict a str json para mysql
    body['observaciones'] = str(json.dumps(body['observaciones']))
    # Uptade
    update = preparation_model.update(nombre, body)
    ex = exception(update)
    if ex:
        return ex
    return {'msg': 'Preparacion actualizada'}, 200


@Preparacion.route('/<nombre>', methods=['DELETE'])
@jwt_required()
def delete_one(nombre):
    if not (nombre):
        return {'error': 'indique el nombre por el path'}, 400
    # sql validations
    if not exists(nombre):
        return {'error': 'Preparacion no existe'}, 400
    # delete
    delete = preparation_model.delete(nombre)
    ex = exception(delete)
    if ex:
        return ex
    return {'msg': 'Preparacion eliminada'}, 200


@Preparacion.route('/set/<set>', methods=['DELETE'])
@jwt_required()
def delete_by_set(set):
    if not (set):
        return {'error': 'indique el student_set por el path'}, 400
    # sql validations
    if not exists_set(set):
        return {'error': 'set no existe'}, 400
    # if not set_preparations(conjun):  return {'error': 'set no tiene preparations'}, 400
    # delete
    delete = preparation_model.delete_set(set)
    ex = exception(delete)
    if ex:
        return ex
    return {'msg': 'preparations del student_set eliminadas'}, 200


def exists(nombre):
    query = preparation_model.get_all()
    if exception(query):
        return False
    lista = map(lambda p: p['nombre'], query)
    return True if nombre in list(lista) else False


def strdate_to_datetime(query):
    for p in query:
        p['fechaInicial'] = str(p['fechaInicial'])
        p['fechaFinal'] = str(p['fechaFinal'])
        # Cambiar formato de campo results desde str json a json
        if p['observaciones']:
            p['observaciones'] = json.loads(p['observaciones'])
    return query
