from flask import request, jsonify, Blueprint
from db.cli.db_cli import DB
from flask_jwt_extended import jwt_required
from utils.utils import *
# Relationsships
from controllers.Programas import exists as exists_programa
import pandas as pd
import json

Estudiante = Blueprint('Estudiante', __name__)

db = DB.getInstance()
# TODO cambiar nombre de tabla
tabla = 'VWDATADESERCION'
# tabla = 'VWDATADESERCIONEIA'
msg_error = { 'msg': 'No hay concidencias' }, 404

##########################################################  VWDATADESERCION ##########################################################

@Estudiante.route('/conjunto/<int:programa>/<int:periodoInicio>/<int:periodoFin>')
@jwt_required()
def get_conjunto_estudiantes(programa, periodoInicio, periodoFin):
    sql = "SELECT * FROM {} WHERE idprograma={} AND REGISTRO >= {} AND REGISTRO <= {} ORDER BY REGISTRO;".format(tabla,programa,periodoInicio, periodoFin)
    query = db.select(sql)
    ex = exception(query)
    if ex: 
        return ex
    if not(query):  return msg_error
    return jsonify(format(query) )

@Estudiante.route('/periodo/<int:periodo>')
@jwt_required()
def get_periodo(periodo):
    sql = 'SELECT * FROM {} WHERE REGISTRO={};'.format(tabla, periodo)
    query = db.select(sql)
    ex = exception(query)
    if ex: 
        return ex
    if not(query):  return msg_error
    return jsonify(format(query) )

@Estudiante.route('/programa/<int:programa>')
@jwt_required()
def get_programa(programa):
    sql = "SELECT * FROM {} WHERE idprograma={};".format(tabla, programa)
    query = db.select(sql)
    ex = exception(query)
    if ex: 
        return ex
    if not(query):  return msg_error
    return jsonify(format(query) )


@Estudiante.route('/programa/<int:programa>/<int:periodo>')
@jwt_required()
def get_periodo_programa(programa, periodo):
    sql = "SELECT * FROM {} WHERE REGISTRO={} and idprograma={}".format(tabla, periodo, programa)
    query = db.select(sql)
    ex = exception(query)
    if ex: 
        return ex
    if not(query):  return msg_error
    return jsonify(format(query))

@Estudiante.route('/documento/<documento>')
@jwt_required()
def get_documento(documento):
    sql = "SELECT * FROM {} WHERE documento='{}';".format(tabla,documento)
    query = db.select(sql)
    ex = exception(query)
    if ex: return ex
    if not(query):  return msg_error
    return jsonify(format(query))


@Estudiante.route('/periodos')
@jwt_required()
def get_periodos():
    # Obtener datos desde la bd SQL server       
    sql = 'SELECT DISTINCT REGISTRO FROM {};'.format(tabla)
    query = db.select(sql)
    ex = exception(query)
    if ex: return ex
    if not query: return msg_error
    periodos_list = [ int(p['REGISTRO']) for p in query]
    periodos =  sorted(periodos_list)
    if not(periodos):  return msg_error
    return jsonify(format(periodos))

@Estudiante.route('/periodos/programa/<int:programa>')
@jwt_required()
def get_periodos_programa(programa):
    # Obtener datos desde la bd SQL server       
    sql = 'SELECT DISTINCT REGISTRO FROM {} WHERE idprograma={};'.format(tabla, programa)
    query = db.select(sql)
    ex = exception(query)
    if ex: return ex
    if not query: return msg_error
    periodos_list = [ int(p['REGISTRO']) for p in query]
    periodos =  sorted(periodos_list)
    if not(periodos):  return msg_error
    return jsonify(format(periodos))

@Estudiante.route('/programas')
@jwt_required()
def get_programas():
    # Obtener datos desde la bd SQL server       
    sql = 'SELECT DISTINCT idprograma, programa FROM {};'.format(tabla)
    query = db.select(sql)
    ex = exception(query)
    if ex: return ex
    if not query: return msg_error
    programas_df = pd.DataFrame(query).sort_values(by='programa', ascending=True)
    programas_df['idprograma'] = programas_df['idprograma'].astype(int)
    programas =  json.loads(programas_df.to_json(orient='records'))
    if not(programas):  return msg_error
    return jsonify(format(programas))
