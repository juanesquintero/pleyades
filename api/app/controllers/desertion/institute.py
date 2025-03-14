from flask import jsonify, Blueprint
from app.db.ies.db import DB
from flask_jwt_extended import jwt_required
from app.utils.utils import exception, _format
# Relaciones
from app.controllers.programs import exists as exists_program
import pandas as pd
import json

IES = Blueprint('IES', __name__)

db = DB.getInstance()
SQL_VIEW = 'VWDATADESERCION'
msg_error = {'msg': 'Not found'}, 404

##########################################################  VWDATADESERCIONINSTITUCION ##########################################################


@IES.route('/<int:period>')
@jwt_required()
def get_period(period: int):
    sql = 'SELECT * FROM {} WHERE periodo={};'.format(SQL_VIEW, period)
    query = db.select(sql)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return msg_error
    return jsonify(_format(query))


@IES.route('/totals/<int:period>')
@jwt_required()
def get_totals_period(period: int):
    sql = 'SELECT sum(desertores) AS desertores, avg(desertion) AS desertion, sum(egresados) AS egresados, sum(mat_hombre) AS mat_hombre, sum(mat_mujer) AS mat_mujer, sum(mat_total) AS mat_total, sum(admi_hombre) AS admi_hombre, sum(admi_mujer) AS admi_mujer, sum(admi_total) AS admi_total, sum(insc_hombre) AS insc_hombre, sum(insc_mujer) AS insc_mujer, sum(insc_total) AS insc_total, sum(mat_nuevos_hombre) AS mat_nuevos_hombre, sum(mat_nuevos_mujer) AS mat_nuevos_mujer, sum(mat_nuevos_total) AS mat_nuevos_total FROM {} WHERE periodo={};'.format(SQL_VIEW, period)
    query = db.select(sql)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return msg_error
    return jsonify(_format(query))


@IES.route('/program/<int:program>')
@jwt_required()
def get_program(program: int):
    sql = "SELECT * FROM {} WHERE idprograma={};".format(SQL_VIEW, program)
    query = db.select(sql)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return msg_error
    return jsonify(_format(query))


@IES.route('/program/<int:program>/<int:period>')
@jwt_required()
def get_period_program(program: int, period: int):
    sql = "SELECT * FROM {} WHERE periodo={} and idprograma={}".format(
        SQL_VIEW, period, program)
    query = db.select(sql)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return msg_error
    return jsonify(_format(query))


@IES.route('/periods')
@jwt_required()
def get_periods():
    # Obtener datos desde the bd SQL server
    sql = 'SELECT DISTINCT period FROM {};'.format(SQL_VIEW)
    query = db.select(sql)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return msg_error
    periods_list = [int(p['period']) for p in query]
    periods = sorted(periods_list)
    if not periods:
        return msg_error
    return jsonify(_format(periods))


@IES.route('/programs')
@jwt_required()
def get_programs():
    # Obtener datos desde the bd SQL server
    sql = 'SELECT DISTINCT idprograma, programa FROM {};'.format(SQL_VIEW)
    query = db.select(sql)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return msg_error
    programs_df = pd.DataFrame(query).sort_values(
        by='programa',
        ascending=True
    )
    programs_df['idprograma'] = programs_df['idprograma'].astype(int)
    programs = json.loads(programs_df.to_json(orient='records'))
    if not programs:
        return msg_error
    return jsonify(_format(programs))


@IES.route('/programs/<int:period>')
@jwt_required()
def get_programs_by_period(period: int):
    # Obtener datos desde the bd SQL server
    sql = 'SELECT DISTINCT idprograma, programa FROM {} WHERE periodo={};'.format(
        SQL_VIEW, period)
    query = db.select(sql)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return msg_error
    programs_df = pd.DataFrame(query).sort_values(
        by='programa',
        ascending=True
    )
    programs_df['idprograma'] = programs_df['idprograma'].astype(int)
    programs = json.loads(programs_df.to_json(orient='records'))
    if not programs:
        return msg_error
    return jsonify(_format(programs))
