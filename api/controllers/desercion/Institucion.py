from flask import request, jsonify, Blueprint
from db.cli.db_cli import DB
from flask_jwt_extended import jwt_required
from utils.utils import *
# Relationsships
from controllers.Programas import exists as exists_programa
import pandas as pd
import json

IES = Blueprint('IES', __name__)

db = DB.getInstance()
tabla = 'VWDATADESERCIONINSTITUCION'
msg_error = { 'msg': 'No hay concidencias' }, 404

##########################################################  VWDATADESERCIONINSTITUCION ##########################################################
@IES.route('/<int:periodo>')
@jwt_required
def get_periodo(periodo: int):
    sql = 'SELECT * FROM {} WHERE periodo={};'.format(tabla, periodo)
    query = db.select(sql)
    ex = exception(query)
    if ex: 
        return ex
    if not(query):  return msg_error
    return jsonify(format(query)) 

@IES.route('/totales/<int:periodo>')
@jwt_required
def get_totales_periodo(periodo: int):
    sql = 'SELECT sum(desertores) AS desertores, avg(desercion) AS desercion, sum(egresados) AS egresados, sum(mat_hombre) AS mat_hombre, sum(mat_mujer) AS mat_mujer, sum(mat_total) AS mat_total, sum(admi_hombre) AS admi_hombre, sum(admi_mujer) AS admi_mujer, sum(admi_total) AS admi_total, sum(insc_hombre) AS insc_hombre, sum(insc_mujer) AS insc_mujer, sum(insc_total) AS insc_total, sum(mat_nuevos_hombre) AS mat_nuevos_hombre, sum(mat_nuevos_mujer) AS mat_nuevos_mujer, sum(mat_nuevos_total) AS mat_nuevos_total FROM {} WHERE periodo={};'.format(tabla, periodo)
    query = db.select(sql)
    ex = exception(query)
    if ex: 
        return ex
    if not(query):  return msg_error
    return jsonify(format(query)) 

@IES.route('/programa/<int:programa>')
@jwt_required
def get_programa(programa: int):
    sql = "SELECT * FROM {} WHERE idprograma={};".format(tabla, programa)
    query = db.select(sql)
    ex = exception(query)
    if ex: 
        return ex
    if not(query):  return msg_error
    return jsonify(format(query)) 

@IES.route('/programa/<int:programa>/<int:periodo>')
@jwt_required
def get_periodo_programa(programa: int, periodo: int):
    sql = "SELECT * FROM {} WHERE periodo={} and idprograma={}".format(tabla, periodo, programa)
    query = db.select(sql)
    ex = exception(query)
    if ex: 
        return ex
    if not(query):  return msg_error
    return jsonify(format(query))

@IES.route('/periodos')
@jwt_required
def get_periodos():
    # Obtener datos desde la bd SQL server       
    sql = 'SELECT DISTINCT periodo FROM {};'.format(tabla)
    query = db.select(sql)
    ex = exception(query)
    if ex: return ex
    if not query: return msg_error
    periodos_list = [ int(p['periodo']) for p in query]
    periodos =  sorted(periodos_list)
    if not(periodos):  return msg_error
    return jsonify(format(periodos))

@IES.route('/programas')
@jwt_required
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
    
@IES.route('/programas/<int:periodo>')
@jwt_required
def get_programas_by_periodo(periodo: int):
    # Obtener datos desde la bd SQL server       
    sql = 'SELECT DISTINCT idprograma, programa FROM {} WHERE periodo={};'.format(tabla, periodo)
    query = db.select(sql)
    ex = exception(query)
    if ex: return ex
    if not query: return msg_error
    programas_df = pd.DataFrame(query).sort_values(by='programa', ascending=True)
    programas_df['idprograma'] = programas_df['idprograma'].astype(int)
    programas =  json.loads(programas_df.to_json(orient='records'))
    if not(programas):  return msg_error
    return jsonify(format(programas))
