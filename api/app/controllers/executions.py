import json
from api.app.utils.constants import Roles
from flask import request, jsonify, Blueprint
from app.schemas.execution_schema import validate_post_schema, validate_put_schema
from flask_jwt_extended import jwt_required
from app.utils.utils import exception, _format
from app.db.pleyades.db import Execution as execution_model
# Relationships
from app.controllers.datasets import exists as exists_set
from app.controllers.users import exists as exists_user

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
        return {'msg': 'No executions'}, 404
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
        return {'msg': 'execution does not exist'}, 404
    query = strdate_to_datetime([query])
    return jsonify(query[0])


@Execution.route('/data_set/<data_set>')
@jwt_required()
def get_by_set(data_set):
    if not exists_set(data_set):
        return {'error': 'data_set does not exist'}, 400
    query = execution_model.get_set(data_set)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'msg': 'data_set has no executions'}, 404
    query = strdate_to_datetime(query)
    return jsonify(query)


@Execution.route('/executor/<executor>')
@jwt_required()
def get_by_user(executor):
    data_set = request.args.get('data_set')
    name = request.args.get('name')
    if not exists_user(executor):
        return {'error': 'user does not exist'}, 400

    if name:
        query = execution_model.get_executor_one(executor, name)
    elif data_set:
        query = execution_model.get_executor_set(executor, data_set)
    else:
        query = execution_model.get_executor(executor)

    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'error': 'user has no executions'}, 400
    query = strdate_to_datetime(query)
    return jsonify(query)


@Execution.route('/name/<data_set>')
@jwt_required()
def name(data_set):
    if not exists_set(data_set):
        return {'error': 'data_set does not exist'}, 400
    # Get the consecutive number for the data_set
    query = execution_model.get_consecutive(data_set)
    ex = exception(query)
    if ex:
        return ex
    if query:
        number = query[0].get('number')+1
    else:
        number = 1
    return {'name': data_set+'.'+str(number), 'number': number}, 200


@Execution.route('', methods=['POST'])
@jwt_required()
def post():
    body = request.get_json()
    # validate schema
    if not validate_post_schema(body):
        return {'error': 'invalid body content'}, 400
    # sql validations
    if not exists_user(body[Roles.EXECUTOR]):
        return {'error': 'user does not exist'}, 404
    if not exists_set(body['data_set']):
        return {'error': 'data_set does not exist'}, 404
    if exists(body['name']):
        return {'error': 'execution already exists'}, 400
    # Change date format
    body['startDate'] = body['startDate'].split('+')[0]
    body['endDate'] = body['endDate'].split('+')[0]
    # Change results field format from dict to json str for mysql
    body['results'] = str(json.dumps(body['results']))
    # Insert
    insert = execution_model.insert(body)
    ex = exception(insert)
    if ex:
        return ex
    return {'msg': 'execution created'}, 200


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
        return {'error': 'Execution does NOT exist'}, 404
    # Change results field format from dict to json str for mysql
    body['results'] = str(json.dumps(body['results']))
    # Update
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
        return {'error': 'Execution does NOT exist'}, 404
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
        return {'error': 'provide the data_set in the path'}, 400
    # sql validations
    if not exists_set(data_set):
        return {'error': 'data_set does not exist'}, 400
    # delete
    delete = execution_model.delete_set(data_set)
    ex = exception(delete)
    if ex:
        return ex
    return {'msg': 'executions of the data_set deleted'}, 200


def exists(name):
    query = execution_model.get_all()
    if exception(query):
        return False
    lista = map(lambda e: e['name'], query)
    return True if name in list(lista) else False


def strdate_to_datetime(query):
    for e in query:
        e['startDate'] = str(e['startDate'])
        e['endDate'] = str(e['endDate'])
        # Change results field format from json str to json
        e['results'] = json.loads(e['results'])
    return query
