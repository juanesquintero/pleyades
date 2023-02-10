from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required
import json
from schemas.preparacionSchema import validate_post_schema, validate_put_schema
from db.pleyades.db import Preparacion as preparacion_model
from utils.utils import *
# Relaciones
from controllers.Conjuntos import exists as exists_conjunto
from controllers.Usuarios import exists as exists_usuario

Preparacion = Blueprint('Preparacion', __name__)

@Preparacion.route('/')
@jwt_required()
def get():
    query = preparacion_model.get_all()
    ex = exception(query)
    if ex: 
        return ex
    if not(query):  
        return {'msg': 'No hay preparaciones'}, 404
    query = strdate_to_datetime(query)
    return jsonify(query) 

@Preparacion.route('/<nombre>')
@jwt_required()
def get_one(nombre):
    query = preparacion_model.get_one(nombre)
    ex = exception(query)
    if ex: 
        return ex
    if not(query):  
        return {'msg': 'No existe la preparación'}, 404
    query = strdate_to_datetime([query])
    return jsonify(query[0]) 

@Preparacion.route('/conjunto/<conjunto>')
@jwt_required()
def get_by_conjunto(conjunto):
    if not exists_conjunto(conjunto): 
        return {'error': 'conjunto no existe'}, 400
    query = preparacion_model.get_conjunto(conjunto)
    ex = exception(query)
    if ex: 
        return ex
    if not(query):  
        return {'msg': 'Conjunto no tiene preparaciones'}, 404
    query = strdate_to_datetime(query)
    return jsonify(query) 

@Preparacion.route('/preparador/<preparador>')
@jwt_required()
def get_by_usuario(preparador):
    if not exists_usuario(preparador): 
        return {'error': 'usuario no existe'}, 400
    query = preparacion_model.get_preparador(preparador)
    ex = exception(query)
    if ex: 
        return ex
    if not(query):  
        return {'error': 'Usuario no tiene preparaciones'}, 400
    query = strdate_to_datetime(query)
    return jsonify(query)

@Preparacion.route('/nombre/<conjunto>')
@jwt_required()
def nombre(conjunto):
    if not exists_conjunto(conjunto): 
        return {'error': 'conjunto no existe'}, 400
    # Obtener el numero consecutivo para el conjunto de datos
    query = preparacion_model.get_consecutivo(conjunto)
    print(query, flush=True)
    ex = exception(query)
    if ex: 
        return ex
    if query:
        numero = query[0].get('numero')+1
    else:
        numero = 1
    return {'nombre': conjunto+'.'+str(numero) , 'numero': numero }, 200

@Preparacion.route('',methods=['POST'])
@jwt_required()
def post():
    body = request.get_json()
    # validate schema
    if not(validate_post_schema(body)): return {'error': 'body invalido'}, 400
    # sql validations
    if not exists_usuario(body['preparador']): 
        return {'error': 'usuario no existe'}, 400
    if not exists_conjunto(body['conjunto']): 
        return {'error': 'conjunto no existe'}, 400
    if exists(body['nombre']): 
        return {'error': 'preparacion ya existe'}, 400
    # Cambiar formato de fechas
    body['fechaInicial'] = body['fechaInicial'].split('+')[0]
    body['fechaFinal'] = body['fechaFinal'].split('+')[0]
    # Cambiar formato de campo observaciones desde dict a str json para mysql
    body['observaciones'] = str( json.dumps(body['observaciones']))
    # Insert 
    insert = preparacion_model.insert(body)
    ex = exception(insert)
    if ex: 
        return ex
    return {'msg': 'Preparacion creada'}, 200

@Preparacion.route('/',methods=['POST'])
@jwt_required()
def post2():
    return post()

@Preparacion.route('/<nombre>',methods=['PUT'])
@jwt_required()
def put(nombre):
    body = request.get_json()
    
    if not(nombre):
        return {'error': 'indique el nombre por el path'}, 400
    # validate schema
    if not(validate_put_schema(body)): 
        return {'error': 'body invalido'}, 400
    # sql validations
    if not exists(nombre):  
        return {'error': 'Preparacion no existe'}, 400
    # Cambiar formato de campo observaciones desde dict a str json para mysql
    body['observaciones'] = str( json.dumps(body['observaciones']))
    # Uptade 
    update = preparacion_model.update(nombre, body)
    ex = exception(update)
    if ex: 
        return ex
    return {'msg': 'Preparacion actualizada'}, 200

@Preparacion.route('/<nombre>',methods=['DELETE'])
@jwt_required()
def delete_one(nombre):
    if not(nombre):
        return {'error': 'indique el nombre por el path'}, 400
    # sql validations
    if not exists(nombre):  return {'error': 'Preparacion no existe'}, 400
    # delete 
    delete = preparacion_model.delete(nombre)
    ex = exception(delete) 
    if ex: 
        return ex
    return {'msg': 'Preparacion eliminada'}, 200

@Preparacion.route('/conjunto/<conjunto>',methods=['DELETE'])
@jwt_required()
def delete_by_conjunto(conjunto):
    if not(conjunto):
        return {'error': 'indique el conjunto por el path'}, 400
    # sql validations
    if not exists_conjunto(conjunto): return {'error': 'conjunto no existe'}, 400
    # if not conjunto_preparaciones(conjun):  return {'error': 'conjunto no tiene preparaciones'}, 400
    # delete 
    delete = preparacion_model.delete_conjunto(conjunto)
    ex = exception(delete) 
    if ex: 
        return ex
    return {'msg': 'preparaciones del conjunto eliminadas'}, 200
    
def exists(nombre):
    query = preparacion_model.get_all()
    if exception(query): 
        return False
    lista = map(lambda p : p['nombre'], query) 
    return True if nombre in list(lista) else False


def strdate_to_datetime(query):
    for p in query: 
        p['fechaInicial']=str(p['fechaInicial'])
        p['fechaFinal']=str(p['fechaFinal'])
        # Cambiar formato de campo resultados desde str json a json
        if p['observaciones']: 
            p['observaciones'] = json.loads(p['observaciones'])
    return query

