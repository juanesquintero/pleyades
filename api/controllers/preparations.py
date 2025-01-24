from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required
import json
from schemas.preparation_schema import validate_post_schema, validate_put_schema
from db.pleyades.db import Preparation as preparation_model
from utils.utils import exception, _format
# Relaciones
from controllers.datasets import exists as exists_set
from controllers.users import exists as exists_usuario

Preparation = Blueprint('Preparation', __name__)


@Preparation.route('')
@Preparation.route('/')
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


@Preparation.route('/<name>')
@jwt_required()
def get_one(name):
    query = preparation_model.get_one(name)
    ex = exception(query)
    if ex:
        return ex
    if not (query):
        return {'msg': 'No existe la preparación'}, 404
    query = strdate_to_datetime([query])
    return jsonify(query[0])


@Preparation.route('/dataset/<dataset>')
@jwt_required()
def get_by_set(dataset):
    if not exists_set(dataset):
        return {'error': 'dataset no existe'}, 400
    query = preparation_model.get_set(dataset)
    ex = exception(query)
    if ex:
        return ex
    if not (query):
        return {'msg': 'Dataset no tiene preparations'}, 404
    query = strdate_to_datetime(query)
    return jsonify(query)


@Preparation.route('/preparador/<preparador>')
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


@Preparation.route('/name/<dataset>')
@jwt_required()
def name(dataset):
    if not exists_set(dataset):
        return {'error': 'dataset no existe'}, 400
    # Obtener el numero consecutivo para el student_set de datos
    query = preparation_model.get_consecutivo(dataset)
    ex = exception(query)
    if ex:
        return ex
    if query:
        numero = query[0].get('numero')+1
    else:
        numero = 1
    return {'name': dataset+'.'+str(numero), 'numero': numero}, 200


@Preparation.route('', methods=['POST'])
@jwt_required()
def post():
    body = request.get_json()
    # validate schema
    if not (validate_post_schema(body)):
        return {'error': 'invalid body content'}, 400
    # sql validations
    if not exists_usuario(body['preparador']):
        return {'error': 'usuario no existe'}, 400
    if not exists_set(body['dataset']):
        return {'error': 'dataset no existe'}, 400
    if exists(body['name']):
        return {'error': 'preparation ya existe'}, 400
    # Cambiar formato de fechas
    body['startDate'] = body['startDate'].split('+')[0]
    body['endDate'] = body['endDate'].split('+')[0]
    # Cambiar formato de campo observaciones desde dict a str json para mysql
    body['observaciones'] = str(json.dumps(body['observaciones']))
    # Insert
    insert = preparation_model.insert(body)
    ex = exception(insert)
    if ex:
        return ex
    return {'msg': 'Preparation creada'}, 200


@Preparation.route('/', methods=['POST'])
@jwt_required()
def post2():
    return post()


@Preparation.route('/<name>', methods=['PUT'])
@jwt_required()
def put(name):
    body = request.get_json()

    if not (name):
        return {'error': 'indique el name por el path'}, 400
    # validate schema
    if not (validate_put_schema(body)):
        return {'error': 'invalid body content'}, 400
    # sql validations
    if not exists(name):
        return {'error': 'Preparation no existe'}, 400
    # Cambiar formato de campo observaciones desde dict a str json para mysql
    body['observaciones'] = str(json.dumps(body['observaciones']))
    # Uptade
    update = preparation_model.update(name, body)
    ex = exception(update)
    if ex:
        return ex
    return {'msg': 'Preparation actualizada'}, 200


@Preparation.route('/<name>', methods=['DELETE'])
@jwt_required()
def delete_one(name):
    if not (name):
        return {'error': 'indique el name por el path'}, 400
    # sql validations
    if not exists(name):
        return {'error': 'Preparation no existe'}, 400
    # delete
    delete = preparation_model.delete(name)
    ex = exception(delete)
    if ex:
        return ex
    return {'msg': 'Preparation eliminada'}, 200


@Preparation.route('/dataset/<dataset>', methods=['DELETE'])
@jwt_required()
def delete_by_set(dataset):
    if not (dataset):
        return {'error': 'indique el student_set por el path'}, 400
    # sql validations
    if not exists_set(dataset):
        return {'error': 'dataset no existe'}, 400
    # if not set_preparations(conjun):  return {'error': 'dataset no tiene preparations'}, 400
    # delete
    delete = preparation_model.delete_set(dataset)
    ex = exception(delete)
    if ex:
        return ex
    return {'msg': 'preparations del student_set eliminadas'}, 200


def exists(name):
    query = preparation_model.get_all()
    if exception(query):
        return False
    lista = map(lambda p: p['name'], query)
    return True if name in list(lista) else False


def strdate_to_datetime(query):
    for p in query:
        p['startDate'] = str(p['startDate'])
        p['endDate'] = str(p['endDate'])
        # Cambiar formato de campo results desde str json a json
        if p['observaciones']:
            p['observaciones'] = json.loads(p['observaciones'])
    return query
