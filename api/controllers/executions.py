import json
from flask import request, jsonify, Blueprint
from schemas.execution_schema import validate_post_schema, validate_put_schema
from flask_jwt_extended import jwt_required
from utils.utils import exception, _format
from db.pleyades.db import Ejecucion as execution_model
# Relaciones
from controllers.sets import exists as exists_set
from controllers.users import exists as exists_usuario

Ejecucion = Blueprint('Ejecucion', __name__)


@Ejecucion.route('')
@Ejecucion.route('/')
@jwt_required()
def get():
    query = execution_model.get_all()
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'msg': 'No hay executions'}, 404
    query = strdate_to_datetime(query)
    return jsonify(query)


@Ejecucion.route('/<nombre>')
@jwt_required()
def get_one(nombre):
    query = execution_model.get_one(nombre)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'msg': 'no existe la ejecución'}, 404
    query = strdate_to_datetime([query])
    return jsonify(query[0])


@Ejecucion.route('/set/<set>')
@jwt_required()
def get_by_set(set):
    if not exists_set(set):
        return {'error': 'set no existe'}, 400
    query = execution_model.get_set(set)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'msg': 'set no tiene executions'}, 404
    query = strdate_to_datetime(query)
    return jsonify(query)


@Ejecucion.route('/ejecutor/<ejecutor>')
@jwt_required()
def get_by_usuario(ejecutor):
    student_set = request.args.get('set')
    nombre = request.args.get('nombre')
    if not exists_usuario(ejecutor):
        return {'error': 'usuario no existe'}, 400

    if nombre:
        query = execution_model.get_ejecutor_one(ejecutor, nombre)
    elif set:
        query = execution_model.get_ejecutor_set(ejecutor, set)
    else:
        query = execution_model.get_ejecutor(ejecutor)

    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'error': 'usuario no tiene executions'}, 400
    query = strdate_to_datetime(query)
    return jsonify(query)


@Ejecucion.route('/nombre/<set>')
@jwt_required()
def nombre(set):
    if not exists_set(set):
        return {'error': 'set no existe'}, 400
    # Obtener el numero consecutivo para el student_set de datos
    query = execution_model.get_consecutivo(set)
    ex = exception(query)
    if ex:
        return ex
    if query:
        numero = query[0].get('numero')+1
    else:
        numero = 1
    return {'nombre': set+'.'+str(numero), 'numero': numero}, 200


@Ejecucion.route('', methods=['POST'])
@jwt_required()
def post():
    body = request.get_json()
    # validate schema
    if not validate_post_schema(body):
        return {'error': 'body invalido'}, 400
    # sql validations
    if not exists_usuario(body['ejecutor']):
        return {'error': 'usuario no existe'}, 404
    if not exists_set(body['set']):
        return {'error': 'set no existe'}, 404
    if exists(body['nombre']):
        return {'error': 'ejecución ya existe'}, 400
    # Cambiar formato de fechas
    body['fechaInicial'] = body['fechaInicial'].split('+')[0]
    body['fechaFinal'] = body['fechaFinal'].split('+')[0]
    # Cambiar formato de campo results desde dict a str json para mysql
    body['results'] = str(json.dumps(body['results']))
    # Insert
    insert = execution_model.insert(body)
    ex = exception(insert)
    if ex:
        return ex
    return {'msg': 'ejecución creada'}, 200


@Ejecucion.route('/', methods=['POST'])
@jwt_required()
def post2():
    return post()


@Ejecucion.route('/<nombre>', methods=['PUT'])
@jwt_required()
def put(nombre):
    body = request.get_json()
    if not nombre:
        return {'error': 'indique el nombre por el path'}, 404
    # validate schema
    if not validate_put_schema(body):
        return {'error': 'body invalido'}, 400
    # sql validations
    if not exists(nombre):
        return {'error': 'Ejecucion no existe'}, 404
    # Cambiar formato de campo results desde dict a str json para mysql
    body['results'] = str(json.dumps(body['results']))
    # Uptade
    update = execution_model.update(nombre, body)
    ex = exception(update)
    if ex:
        return ex
    return {'msg': 'Ejecucion actualizada'}, 200


@Ejecucion.route('/<nombre>', methods=['DELETE'])
@jwt_required()
def delete_one(nombre):
    if not nombre:
        return {'error': 'indique el nombre por el path'}, 404
    # sql validations
    if not exists(nombre):
        return {'error': 'Ejecucion no existe'}, 404
    # delete
    delete = execution_model.delete(nombre)
    ex = exception(delete)
    if ex:
        return ex
    return {'msg': 'Ejecucion eliminada'}, 200


@Ejecucion.route('/set/<set>', methods=['DELETE'])
@jwt_required()
def delete_by_set(set):
    if not set:
        return {'error': 'indique el student_set por el path'}, 400
    # sql validations
    if not exists_set(set):
        return {'error': 'set no existe'}, 400
    # if not set_preparations(conjun):  return {'error': "set no tiene preparations"}, 400
    # delete
    delete = execution_model.delete_set(set)
    ex = exception(delete)
    if ex:
        return ex
    return {'msg': 'executions del student_set eliminadas'}, 200


def exists(nombre):
    query = execution_model.get_all()
    if exception(query):
        return False
    lista = map(lambda e: e['nombre'], query)
    return True if nombre in list(lista) else False


def strdate_to_datetime(query):
    for e in query:
        e['fechaInicial'] = str(e['fechaInicial'])
        e['fechaFinal'] = str(e['fechaFinal'])
        # Cambiar formato de campo results desde str json a json
        e['results'] = json.loads(e['results'])
    return query
