import json
from flask import request, jsonify, Blueprint
from schemas.execution_schema import validate_post_schema, validate_put_schema
from flask_jwt_extended import jwt_required
from utils.utils import exception, _format
from db.pleyades.db import Execution as execution_model
# Relaciones
from controllers.datasets import exists as exists_set
from controllers.users import exists as exists_usuario

Execution = Blueprint('Execution', __name__)


@Execution.route('')
@Execution.route('/')
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


@Execution.route('/<name>')
@jwt_required()
def get_one(name):
    query = execution_model.get_one(name)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'msg': 'no existe la ejecución'}, 404
    query = strdate_to_datetime([query])
    return jsonify(query[0])


@Execution.route('/data_set/<data_set>')
@jwt_required()
def get_by_set(data_set):
    if not exists_set(data_set):
        return {'error': 'data_set no existe'}, 400
    query = execution_model.get_set(data_set)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'msg': 'data_set no tiene executions'}, 404
    query = strdate_to_datetime(query)
    return jsonify(query)


@Execution.route('/ejecutor/<ejecutor>')
@jwt_required()
def get_by_usuario(ejecutor):
    data_set = request.args.get('data_set')
    name = request.args.get('name')
    if not exists_usuario(ejecutor):
        return {'error': 'usuario no existe'}, 400

    if name:
        query = execution_model.get_ejecutor_one(ejecutor, name)
    elif data_set:
        query = execution_model.get_ejecutor_set(ejecutor, data_set)
    else:
        query = execution_model.get_ejecutor(ejecutor)

    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'error': 'usuario no tiene executions'}, 400
    query = strdate_to_datetime(query)
    return jsonify(query)


@Execution.route('/name/<data_set>')
@jwt_required()
def name(data_set):
    if not exists_set(data_set):
        return {'error': 'data_set no existe'}, 400
    # Obtener el numero consecutivo para el data_set de datos
    query = execution_model.get_consecutivo(data_set)
    ex = exception(query)
    if ex:
        return ex
    if query:
        numero = query[0].get('numero')+1
    else:
        numero = 1
    return {'name': data_set+'.'+str(numero), 'numero': numero}, 200


@Execution.route('', methods=['POST'])
@jwt_required()
def post():
    body = request.get_json()
    # validate schema
    if not validate_post_schema(body):
        return {'error': 'invalid body content'}, 400
    # sql validations
    if not exists_usuario(body['ejecutor']):
        return {'error': 'usuario no existe'}, 404
    if not exists_set(body['data_set']):
        return {'error': 'data_set no existe'}, 404
    if exists(body['name']):
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


@Execution.route('/', methods=['POST'])
@jwt_required()
def post2():
    return post()


@Execution.route('/<name>', methods=['PUT'])
@jwt_required()
def put(name):
    body = request.get_json()
    if not name:
        return {'error': 'provide the name in the path'}, 404
    # validate schema
    if not validate_put_schema(body):
        return {'error': 'invalid body'}, 400
    # sql validations
    if not exists(name):
        return {'error': 'Execution does NOT exists'}, 404
    # Cambiar formato de campo results desde dict a str json para mysql
    body['results'] = str(json.dumps(body['results']))
    # Uptade
    update = execution_model.update(name, body)
    ex = exception(update)
    if ex:
        return ex
    return {'msg': 'Execution updated'}, 200


@Execution.route('/<name>', methods=['DELETE'])
@jwt_required()
def delete_one(name):
    if not name:
        return {'error': 'provide the name in the path'}, 404
    # sql validations
    if not exists(name):
        return {'error': 'Execution NOT exists'}, 404
    # delete
    delete = execution_model.delete(name)
    ex = exception(delete)
    if ex:
        return ex
    return {'msg': 'Execution deleted'}, 200


@Execution.route('/data_set/<data_set>', methods=['DELETE'])
@jwt_required()
def delete_by_set(data_set):
    if not data_set:
        return {'error': 'indique el data_set por el path'}, 400
    # sql validations
    if not exists_set(data_set):
        return {'error': 'data_set no existe'}, 400
    # if not set_preparations(conjun):  return {'error': "data_set no tiene preparations"}, 400
    # delete
    delete = execution_model.delete_set(data_set)
    ex = exception(delete)
    if ex:
        return ex
    return {'msg': 'executions del data_set eliminadas'}, 200


def exists(name):
    query = execution_model.get_all()
    if exception(query):
        return False
    lista = map(lambda e: e['name'], query)
    return True if name in list(lista) else False


def strdate_to_datetime(query):
    for e in query:
        e['fechaInicial'] = str(e['fechaInicial'])
        e['fechaFinal'] = str(e['fechaFinal'])
        # Cambiar formato de campo results desde str json a json
        e['results'] = json.loads(e['results'])
    return query
