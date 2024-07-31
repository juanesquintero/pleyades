from flask import request, jsonify, Blueprint
from db.ies.db import DB as db_ies
from db.pleyades.db import Conjunto as conjunto_model, Ejecucion as ejecucion_model, Preparacion as preparacion_model
from schemas.conjunto_schema import validate_post_schema, validate_put_schema, validate_nombre_schema
from flask_jwt_extended import jwt_required
from utils.utils import exception, _format

# Relaciones
from controllers.Programas import exists as exists_programa
from controllers.Usuarios import exists as exists_usuario

Conjunto = Blueprint('Conjunto', __name__)
execute = None
db_ies = db_ies.getInstance()


@Conjunto.route('')
@Conjunto.route('/')
@jwt_required()
def get():
    query = conjunto_model.get_all()
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'msg': 'No hay Conjuntos'}, 404
    return jsonify(query)


@Conjunto.route('/<nombre>')
@jwt_required()
def get_one(nombre):
    query = conjunto_model.get_one(nombre)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'msg': 'No hay concidencias'}, 404
    return jsonify(query)


@Conjunto.route('/estado/<estado>')
@jwt_required()
def get_by_estado(estado):
    query = conjunto_model.get_estado(estado)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'msg': 'No hay concidencias'}, 404
    return jsonify(query)


@Conjunto.route('/tipo/<tipo>')
@jwt_required()
def get_by_tipo(tipo):
    query = conjunto_model.get_tipo(tipo)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'msg': 'No hay concidencias'}, 404
    return jsonify(query)


@Conjunto.route('/programa/<int:programa>')
@jwt_required()
def get_by_programa(programa):
    query = conjunto_model.get_programa(programa)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'msg': 'No hay concidencias'}, 404
    return jsonify(query)


@Conjunto.route('encargado/<encargado>')
@jwt_required()
def get_by_encargado(encargado):
    estado = request.args.get('estado')
    if estado:
        if estado.lower().strip() in ['crudos', 'procesados', 'en proceso']:
            query = conjunto_model.get_encargado(encargado, estado)
        else:
            return {'msg': 'Estado invalido'}, 404
    else:
        query = conjunto_model.get_encargado(encargado)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'msg': 'No hay concidencias'}, 404
    return jsonify(query)


@Conjunto.route('/periodos/<int:inicio>/<int:fin>')
@jwt_required()
def get_by_periodos(inicio, fin):
    query = conjunto_model.get_rango(inicio, fin)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'msg': 'No hay concidencias'}, 404
    return jsonify(query)


@Conjunto.route('', methods=['POST'])
@jwt_required()
def post():
    body = request.get_json()
    # validate schema
    if not(validate_post_schema(body)):
        return {'error': 'body invalido'}, 400
    # Logical Validations
    if body['periodoInicial'] > body['periodoFinal']:
        return {'error': 'Periodo Inicial no puede ser mayor al Final'}, 400
    # sql validations
    if exists(body['nombre']):
        return {'error': 'Conjunto Ya existe'}, 400
    if not exists_usuario(body['encargado']):
        return {'error': 'usuario no existe'}, 400
    if not exists_programa(body['programa']):
        return {'error': 'programa no existe'}, 400
    if not body['estado'] in ['Crudos', 'Procesados', 'En Proceso']:
        return {'error': 'estado invalido'}, 400
    # Insert
    insert = conjunto_model.insert(body)
    ex = exception(insert)
    if ex:
        return ex
    return {'msg': 'Conjunto creado'}, 200


@Conjunto.route('/', methods=['POST'])
@jwt_required()
def post2():
    return post()


@Conjunto.route('/nombre', methods=['POST'])
@jwt_required()
def nombre():
    body = request.get_json()
    # validate schema
    if not validate_nombre_schema(body):
        return {'error': 'body invalido'}, 400
    # sql validations
    if not exists_usuario(body['encargado']):
        return {'error': 'usuario no existe'}, 400
    if not exists_programa(body['programa']):
        return {'error': 'programa no existe'}, 400
    if not body['estado'] in ['Crudos', 'Procesados', 'En Proceso']:
        return {'error': 'estado invalido'}, 400
    if not body['tipo'] in ['consulta', 'excel']:
        return {'error': 'tipo invalido'}, 400
    # Obtener el numero consecutivo para el conjunto de datos
    query = conjunto_model.get_numero(
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
    # Obtener la sigla del nombre del programa
    programa = db_ies.select(
        'SELECT * FROM VWPROGRAMADESERCION WHERE codigo={};'.format(str(body['programa'])))
    ex = exception(programa)
    if ex:
        return ex
    nombre_corto = programa[0]['nombre_corto']
    # Definir el nombre del conjunto con la notacion
    nombre = nombre_corto+' ' + \
        str(body['periodoInicial'])+' ' + \
        str(body['periodoFinal'])+' '+str(numero)

    return {'nombre': nombre, 'numero': numero}, 200



@Conjunto.route('/todos/<estado>', methods=['DELETE'])
@jwt_required()
def delete_many(estado):
    if not(estado):
        return {'error': 'indique el estado por el path'}, 400
    estado = estado.title()
    query = conjunto_model.get_estado(estado)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return {'msg': 'No hay concidencias'}, 404

    conjuntos_nombres = [ c['nombre'] for c in query]
    for conjunto in conjuntos_nombres:
        # delete conjunto
        delete = conjunto_model.delete(conjunto)
        # delete resultados
        delete = ejecucion_model.delete_conjunto(conjunto)
        delete = preparacion_model.delete_conjunto(conjunto)
        ex = exception(delete)
        if ex:
            return ex

    return {'msg': 'Conjuntos eliminados', 'data': conjuntos_nombres}, 200

@Conjunto.route('/<nombre>', methods=['DELETE'])
@jwt_required()
def delete_one(nombre):
    if not(nombre):
        return {'error': 'indique el nombre por el path'}, 400
    # sql validations
    if not exists(nombre):
        return {'error': 'Conjunto no existe'}, 404
    # delete
    delete = conjunto_model.delete(nombre)
    # delete resultados
    delete = ejecucion_model.delete_conjunto(nombre)
    delete = preparacion_model.delete_conjunto(nombre)
    ex = exception(delete)
    if ex:
        return ex
    return {'msg': 'Conjunto eliminado'}, 200


@Conjunto.route('/<nombre>', methods=['PUT'])
@jwt_required()
def put(nombre):
    body = request.get_json()
    if not(nombre):
        return {'error': 'indique el nombre por el path'}, 404
    # validate schema
    if not(validate_put_schema(body)):
        return {'error': 'body invalido'}, 400
    # sql validations
    if not exists(nombre):
        return {'error': 'Conjunto no existe'}, 404
    if 'estado' in body.keys():
        if not body['estado'] in ['Crudos', 'Procesados', 'En Proceso']:
            return {'error': 'estado invalido'}, 400
    if 'encargado' in body.keys():
        if not exists_usuario(body['encargado']):
            return {'error': 'encargado invalido'}, 400
    # Uptade
    update = conjunto_model.update(nombre, body)
    ex = exception(update)
    if ex:
        return ex
    return {'msg': 'Conjunto actualizado'}, 200


def exists(nombre):
    query = conjunto_model.get_all()
    if exception(query):
        return False
    lista = map(lambda c: c['nombre'], query)
    return True if nombre in list(lista) else False
