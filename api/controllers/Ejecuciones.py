import json
from flask import request, jsonify, Blueprint
from schemas.ejecucion_schema import validate_post_schema, validate_put_schema
from flask_jwt_extended import jwt_required
from utils.utils import exception, _format
from db.pleyades.db import Ejecucion as ejecucion_model
# Relaciones
from controllers.Conjuntos import exists as exists_conjunto
from controllers.Usuarios import exists as exists_usuario

Ejecucion = Blueprint('Ejecucion', __name__)

@Ejecucion.route('')
@Ejecucion.route('/')
@jwt_required()
def get():
    query = ejecucion_model.get_all()
    ex = exception(query)
    if ex: 
        return ex
    if not(query):  
        return {'msg': 'No hay ejecuciones'}, 404
    query = strdate_to_datetime(query)
    return jsonify(query) 

@Ejecucion.route('/<nombre>')
@jwt_required()
def get_one(nombre):
    query = ejecucion_model.get_one(nombre)
    ex = exception(query)
    if ex: 
        return ex
    if not(query):  
        return {'msg': 'no existe la ejecución'}, 404
    query = strdate_to_datetime([query])
    return jsonify(query[0]) 

@Ejecucion.route('/conjunto/<conjunto>')
@jwt_required()
def get_by_conjunto(conjunto):
    if not exists_conjunto(conjunto): 
        return {'error': 'conjunto no existe'}, 400
    query = ejecucion_model.get_conjunto(conjunto)
    ex = exception(query)
    if ex: 
        return ex
    if not(query):  
        return {'msg': 'conjunto no tiene ejecuciones'}, 404
    query = strdate_to_datetime(query)
    return jsonify(query) 

@Ejecucion.route('/ejecutor/<ejecutor>')
@jwt_required()
def get_by_usuario(ejecutor):
    if not exists_usuario(ejecutor): 
        return {'error': 'usuario no existe'}, 400
    query = ejecucion_model.get_ejecutor(ejecutor)
    ex = exception(query)
    if ex: 
        return ex
    if not(query):  
        return {'error': 'usuario no tiene ejecuciones'}, 400
    query = strdate_to_datetime(query)
    return jsonify(query)

@Ejecucion.route('/nombre/<conjunto>')
@jwt_required()
def nombre(conjunto):
    if not exists_conjunto(conjunto): 
        return {'error': 'conjunto no existe'}, 400
    # Obtener el numero consecutivo para el conjunto de datos
    query = ejecucion_model.get_consecutivo(conjunto)
    ex = exception(query)
    if ex: 
        return ex
    if query:
        numero = query[0].get('numero')+1
    else:
        numero = 1
    return {'nombre': conjunto+'.'+str(numero) , 'numero': numero }, 200

@Ejecucion.route('',methods=['POST'])
@jwt_required()
def post():
    body = request.get_json()
    # validate schema
    if not(validate_post_schema(body)): 
        return {'error': 'body invalido'}, 400
    # sql validations
    if not exists_usuario(body['ejecutor']): 
        return {'error': 'usuario no existe'}, 404
    if not exists_conjunto(body['conjunto']): 
        return {'error': 'conjunto no existe'}, 404
    if exists(body['nombre']): 
        return {'error': 'ejecución ya existe'}, 400
    # Cambiar formato de fechas
    body['fechaInicial'] = body['fechaInicial'].split('+')[0]
    body['fechaFinal'] = body['fechaFinal'].split('+')[0]
    # Cambiar formato de campo resultados desde dict a str json para mysql
    body['resultados'] = str( json.dumps(body['resultados']))
    # Insert
    insert = ejecucion_model.insert(body)
    ex = exception(insert)
    if ex: 
        return ex
    return {'msg': 'ejecución creada'}, 200

@Ejecucion.route('/',methods=['POST'])
@jwt_required()
def post2():
    return post()

@Ejecucion.route('/<nombre>',methods=['PUT'])
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
        return {'error': 'Ejecucion no existe'}, 404
    # Cambiar formato de campo resultados desde dict a str json para mysql
    body['resultados'] = str( json.dumps(body['resultados']))
    # Uptade 
    update = ejecucion_model.update(nombre, body)
    ex = exception(update)
    if ex: 
        return ex
    return {'msg': 'Ejecucion actualizada'}, 200

@Ejecucion.route('/<nombre>',methods=['DELETE'])
@jwt_required()
def delete_one(nombre):
    if not(nombre):
        return {'error': 'indique el nombre por el path'}, 404
    # sql validations
    if not exists(nombre):  
        return {'error': 'Ejecucion no existe'}, 404
    # delete 
    delete = ejecucion_model.delete(nombre)
    ex = exception(delete) 
    if ex: 
        return ex
    return {'msg': 'Ejecucion eliminada'}, 200

@Ejecucion.route('/conjunto/<conjunto>',methods=['DELETE'])
@jwt_required()
def delete_by_conjunto(conjunto):
    if not(conjunto):
        return {'error': 'indique el conjunto por el path'}, 400
    # sql validations
    if not exists_conjunto(conjunto): return {'error': 'conjunto no existe'}, 400
    # if not conjunto_preparaciones(conjun):  return {'error': "conjunto no tiene preparaciones"}, 400
    # delete 
    delete = ejecucion_model.delete_conjunto(conjunto)
    ex = exception(delete) 
    if ex: 
        return ex
    return {'msg': 'ejecuciones del conjunto eliminadas'}, 200

def exists(nombre):
    query = ejecucion_model.get_all()
    if exception(query): 
        return False
    lista = map(lambda e : e['nombre'], query) 
    return True if nombre in list(lista) else False

def strdate_to_datetime(query):
    for e in query: 
        e['fechaInicial']=str(e['fechaInicial'])
        e['fechaFinal']=str(e['fechaFinal'])
        # Cambiar formato de campo resultados desde str json a json
        e['resultados'] = json.loads(e['resultados'])
    return query