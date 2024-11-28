from flask import request, jsonify, Blueprint
from db.ies.db import DB as db_ies
from db.pleyades.db import Dataset as dataset_model, Execution as execution_model, Preparation as preparation_model
from schemas.dataset_schema import validate_post_schema, validate_put_schema, validate_nombre_schema
from flask_jwt_extended import jwt_required
from utils.utils import exception, _format

# Relaciones
from controllers.programs import exists as exists_program
from controllers.users import exists as exists_usuario

Dataset = Blueprint('Dataset', __name__)
execute = None
db_ies = db_ies.getInstance()


@Dataset.route('')
@Dataset.route('/')
@jwt_required()
def get():
    query = dataset_model.get_all()
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'msg': 'No hay Datasets'}, 404
    return jsonify(query)


@Dataset.route('/<name>')
@jwt_required()
def get_one(name):
    query = dataset_model.get_one(name)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'msg': 'No hay concidencias'}, 404
    return jsonify(query)


@Dataset.route('/estado/<estado>')
@jwt_required()
def get_by_state(estado):
    query = dataset_model.get_state(estado)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'msg': 'No hay concidencias'}, 404
    return jsonify(query)


@Dataset.route('/tipo/<tipo>')
@jwt_required()
def get_by_tipo(tipo):
    query = dataset_model.get_tipo(tipo)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'msg': 'No hay concidencias'}, 404
    return jsonify(query)


@Dataset.route('/programa/<int:programa>')
@jwt_required()
def get_by_program(programa):
    query = dataset_model.get_program(programa)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'msg': 'No hay concidencias'}, 404
    return jsonify(query)


@Dataset.route('encargado/<encargado>')
@jwt_required()
def get_by_encargado(encargado):
    estado = request.args.get('estado')
    if estado:
        if estado.lower().strip() in ['crudos', 'procesados', 'en proceso']:
            query = dataset_model.get_encargado(encargado, estado)
        else:
            return {'msg': 'Estado invalido'}, 404
    else:
        query = dataset_model.get_encargado(encargado)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'msg': 'No hay concidencias'}, 404
    return jsonify(query)


@Dataset.route('/periods/<int:inicio>/<int:fin>')
@jwt_required()
def get_by_periods(inicio, fin):
    query = dataset_model.get_rango(inicio, fin)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'msg': 'No hay concidencias'}, 404
    return jsonify(query)


@Dataset.route('', methods=['POST'])
@jwt_required()
def post():
    body = request.get_json()
    # validate schema
    if not (validate_post_schema(body)):
        return {'error': 'invalid body content'}, 400
    # Logical Validations
    if body['periodoInicial'] > body['periodoFinal']:
        return {'error': 'Periodo Inicial no puede ser mayor al Final'}, 400
    # sql validations
    if exists(body['name']):
        return {'error': 'Dataset Ya existe'}, 400
    if not exists_usuario(body['encargado']):
        return {'error': 'usuario no existe'}, 400
    if not exists_program(body['programa']):
        return {'error': 'programa no existe'}, 400
    if not body['estado'] in ['Crudos', 'Procesados', 'En Proceso']:
        return {'error': 'estado invalido'}, 400
    # Insert
    insert = dataset_model.insert(body)
    ex = exception(insert)
    if ex:
        return ex
    return {'msg': 'Dataset created'}, 200


@Dataset.route('/', methods=['POST'])
@jwt_required()
def post2():
    return post()


@Dataset.route('/name', methods=['POST'])
@jwt_required()
def name():
    body = request.get_json()
    # validate schema
    if not validate_nombre_schema(body):
        return {'error': 'invalid body content'}, 400
    # sql validations
    if not exists_usuario(body['encargado']):
        return {'error': 'usuario no existe'}, 400
    if not exists_program(body['programa']):
        return {'error': 'programa no existe'}, 400
    if not body['estado'] in ['Crudos', 'Procesados', 'En Proceso']:
        return {'error': 'estado invalido'}, 400
    if not body['tipo'] in ['consulta', 'excel']:
        return {'error': 'tipo invalido'}, 400
    # Obtener el numero consecutivo para el student_dataset de datos
    query = dataset_model.get_numero(
        body['programa'],
        body['periodoInicial'],
        body['periodoFinal']
    )
    ex = exception(query)
    if ex:
        return ex
    if query:
        numero = query[0].get('numero')+1
    else:
        numero = 1
    # Obtener la sigla del name del programa
    programa = db_ies.select(
        'SELECT * FROM VWPROGRAMADESERCION WHERE codigo={};'.format(str(body['programa'])))
    ex = exception(programa)
    if ex:
        return ex
    nombre_corto = programa[0]['nombre_corto']
    # Definir el name del student_dataset con la notacion
    name = nombre_corto+' ' + \
        str(body['periodoInicial'])+' ' + \
        str(body['periodoFinal'])+' '+str(numero)

    return {'name': name, 'numero': numero}, 200


@Dataset.route('/todos/<estado>', methods=['DELETE'])
@jwt_required()
def delete_many(estado):
    if not (estado):
        return {'error': 'indique el estado por el path'}, 400
    estado = estado.title()
    query = dataset_model.get_state(estado)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'msg': 'No hay concidencias'}, 404

    datasets_nombres = [c['name'] for c in query]
    for student_dataset in datasets_nombres:
        # delete dataset
        delete = dataset_model.delete(dataset)
        # delete results
        delete = execution_model.delete_dataset(dataset)
        delete = preparation_model.delete_dataset(dataset)
        ex = exception(delete)
        if ex:
            return ex

    return {'msg': 'Datasets eliminados', 'data': datasets_nombres}, 200


@Dataset.route('/<name>', methods=['DELETE'])
@jwt_required()
def delete_one(name):
    if not (name):
        return {'error': 'indique el name por el path'}, 400
    # sql validations
    if not exists(name):
        return {'error': 'Dataset no existe'}, 404
    # delete
    delete = dataset_model.delete(name)
    # delete results
    delete = execution_model.delete_dataset(name)
    delete = preparation_model.delete_dataset(name)
    ex = exception(delete)
    if ex:
        return ex
    return {'msg': 'Dataset eliminado'}, 200


@Dataset.route('/<name>', methods=['PUT'])
@jwt_required()
def put(name):
    body = request.get_json()
    if not (name):
        return {'error': 'indique el name por el path'}, 404
    # validate schema
    if not (validate_put_schema(body)):
        return {'error': 'invalid body content'}, 400
    # sql validations
    if not exists(name):
        return {'error': 'Dataset no existe'}, 404
    if 'estado' in body.keys():
        if not body['estado'] in ['Crudos', 'Procesados', 'En Proceso']:
            return {'error': 'estado invalido'}, 400
    if 'encargado' in body.keys():
        if not exists_usuario(body['encargado']):
            return {'error': 'encargado invalido'}, 400
    # Uptade
    update = dataset_model.update(name, body)
    ex = exception(update)
    if ex:
        return ex
    return {'msg': 'Dataset actualizado'}, 200


def exists(name):
    query = dataset_model.get_all()
    if exception(query):
        return False
    lista = map(lambda c: c['name'], query)
    return True if name in list(lista) else False
