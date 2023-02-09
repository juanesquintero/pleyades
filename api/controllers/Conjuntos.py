from flask import request, jsonify, Blueprint
from db.pleyades.db import DB
from db.cli.db_cli import DB as db_cli
from schemas.conjuntoSchema import validate_post_schema, validate_put_schema, validate_nombre_schema
from flask_jwt_extended import jwt_required
from utils.utils import *
# Relationsships
from controllers.Programas import exists as exists_programa
from controllers.Usuarios import exists as exists_usuario

Conjunto = Blueprint('Conjunto', __name__)
  
db = DB.getInstance()
db_cli = db_cli.getInstance()

@Conjunto.route('/')
@jwt_required()
def get():
    query = db.select('SELECT * FROM conjuntosdedatos;')
    ex = exception(query)
    if ex: 
        return ex
    if not(query):  return {'msg': 'No hay Conjuntos'}, 404
    return jsonify(query) 

@Conjunto.route('/<nombre>')
@jwt_required()
def getOne(nombre):
    query = db.select("SELECT * FROM conjuntosdedatos WHERE nombre='{}';".format(nombre))
    ex = exception(query)
    if ex: 
        return ex
    if not(query):  return {'msg': 'No hay concidencias'}, 404
    return jsonify(query) 


@Conjunto.route('/estado/<estado>')
@jwt_required()
def getByEstado(estado):
    query = db.select("SELECT * FROM conjuntosdedatos WHERE estado='{}';".format(estado))
    ex = exception(query)
    if ex: 
        return ex
    if not(query):  return {'msg': 'No hay concidencias'}, 404
    return jsonify(query) 

@Conjunto.route('/tipo/<tipo>')
@jwt_required()
def getByTipo(tipo):
    query = db.select("SELECT * FROM conjuntosdedatos WHERE tipo='{}';".format(tipo))
    ex = exception(query)
    if ex: 
        return ex
    if not(query):
        return {'msg': 'No hay concidencias'}, 404
    return jsonify(query) 

@Conjunto.route('/programa/<int:programa>')
@jwt_required()
def getByPrograma(programa):
    query = db.select('SELECT * FROM conjuntosdedatos WHERE programa={};'.format(str(programa)))
    ex = exception(query)
    if ex: 
        return ex
    if not(query):  
        return {'msg': 'No hay concidencias'}, 404
    return jsonify(query)

@Conjunto.route('encargado/<encargado>')
@jwt_required()
def getByEncargado(encargado):
    estado = request.args.get('estado')
    if estado:
        if estado.lower().strip() in ['crudos', 'procesados', 'en proceso']:
            query = db.select("SELECT * FROM conjuntosdedatos WHERE encargado='{}' AND estado='{}';".format(encargado,estado))
        else:
            return {'msg': 'Estado invalido'}, 404
    else:
        query = db.select("SELECT * FROM conjuntosdedatos WHERE encargado='{}';".format(encargado))
    ex = exception(query)
    if ex: 
        return ex
    if not(query):  
        return {'msg': 'No hay concidencias'}, 404
    return jsonify(query)


@Conjunto.route('/periodos/<int:inicio>/<int:fin>')
@jwt_required()
def getByPeriodos(inicio, fin):
    query = db.select('SELECT * FROM conjuntosdedatos WHERE periodoInicial={} AND periodoFinal={};'.format(inicio,fin))
    ex = exception(query)
    if ex: 
        return ex
    if not(query):  return {'msg': 'No hay concidencias'}, 404
    return jsonify(query) 

@Conjunto.route('',methods=['POST'])
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
    if not body['estado'] in ['Crudos','Procesados','En Proceso']: 
        return {'error': 'estado invalido'}, 400  
    # Insert 
    insert = db.insert(body,'conjuntosdedatos')
    ex = exception(insert)
    if ex: 
        return ex
    return {'msg': 'Conjunto creado'}, 200

@Conjunto.route('/',methods=['POST'])
@jwt_required()
def post2():
    return post()

@Conjunto.route('/nombre',methods=['POST'])
@jwt_required()
def nombre():
    body = request.get_json()
    # validate schema
    if not(validate_nombre_schema(body)):
        return {'error': 'body invalido'}, 400
    # sql validations
    if not exists_usuario(body['encargado']): 
        return {'error': 'usuario no existe'}, 400
    if not exists_programa(body['programa']): 
        return {'error': 'programa no existe'}, 400
    if not body['estado'] in ['Crudos','Procesados','En Proceso']: 
        return {'error': 'estado invalido'}, 400
    if not body['tipo'] in ['consulta','excel']: 
        return {'error': 'tipo invalido'}, 400  
    # Obtener el numero consecutivo para el conjunto de datos
    sql = 'SELECT * FROM conjuntosdedatos WHERE programa={} AND periodoInicial={} AND periodoFinal={} ORDER BY numero DESC;'
    query = db.select(sql.format(str(body['programa']),str(body['periodoInicial']),str(body['periodoFinal'])))
    ex = exception(query)
    if ex: 
        return ex
    if query:
        numero = query[0]['numero']+1
    else:
        numero = 1
    # Obtener la sigla del nombre del programa
    programa = db_cli.select('SELECT * FROM VWPROGRAMADESERCION WHERE codigo={};'.format(str(body['programa'])))
    ex = exception(programa)
    if ex: 
        return ex
    nombre_corto = programa[0]['nombre_corto']
    # Definir el nombre del conjunto con la notacion 
    nombre = nombre_corto+' '+str(body['periodoInicial'])+' '+str(body['periodoFinal'])+' '+str(numero)
    
    return {'nombre': nombre, 'numero': numero }, 200


@Conjunto.route('/<nombre>',methods=['DELETE'])
@jwt_required()
def deleteOne(nombre):
    if not(nombre):
        return {'error': 'indique el nombre por el path'}, 400
    # sql validations
    if not exists(nombre):
        return {'error': 'Conjunto no existe'}, 404
    # delete 
    condicion="nombre='"+nombre+"'"
    delete = db.delete(condicion,'conjuntosdedatos')
    # delete resultados
    condicion_resultados="conjunto='"+nombre+"'"
    delete = db.delete(condicion_resultados,'ejecuciones')
    delete = db.delete(condicion_resultados,'preparaciones')
    ex = exception(delete) 
    if ex: 
        return ex
    return {'msg': 'Conjunto eliminado'}, 200

@Conjunto.route('/<nombre>',methods=['PUT'])
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
        if not body['estado'] in ['Crudos','Procesados','En Proceso']: 
            return {'error': 'estado invalido'}, 400 
    if 'encargado' in body.keys():
        if not exists_usuario(body['encargado']): 
            return {'error': 'encargado invalido'}, 400  
    # Uptade 
    condicion="nombre='"+nombre+"'"
    update = db.update(body,condicion,'conjuntosdedatos')
    ex = exception(update) 
    if ex: 
        return ex
    return {'msg': 'Conjunto actualizado'}, 200

def exists(nombre):
    error_logger.error('Nombre "{}"'.format(nombre))
    query = db.select('SELECT * FROM conjuntosdedatos;')
    error_logger.error('QUERY: ' + query.__str__())
    if exception(query): 
        return False
    lista = map(lambda c : c['nombre'], query) 
    return True if nombre in list(lista) else False

# Funcion que retiorna una sigla optima para el nombre del programa
def sigla_programa(nombre):
    pass

