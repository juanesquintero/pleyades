import json
import pandas as pd
from flask_jwt_extended import jwt_required
from flask import request, jsonify, Blueprint

from db.ies.db import DB
from utils.utils import exception, _format
from controllers.programs import exists as exists_program

Student = Blueprint('Student', __name__)

db = DB.getInstance()

table = 'VWDATADESERCION'

msg_error = {'msg': 'Not found'}, 404

##########################################################  VWDATADESERCION ##########################################################


@Student.route('/dataset/<int:program>/<int:periodInicio>/<int:periodFin>')
@jwt_required()
def get_set_estudiantes(program, periodInicio, periodFin):
    sql = f'SELECT * FROM {table} WHERE idprograma={program} AND REGISTRO >= {
        periodInicio} AND REGISTRO <= {periodFin} ORDER BY REGISTRO;'
    query = db.select(sql)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return msg_error
    return jsonify(_format(query))


@Student.route('/period/<int:period>')
@jwt_required()
def get_period(period):
    sql = f'SELECT * FROM {table} WHERE REGISTRO={period};'
    query = db.select(sql)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return msg_error
    return jsonify(_format(query))


@Student.route('/program/<int:program>')
@jwt_required()
def get_program(program):
    sql = f"SELECT * FROM {table} WHERE idprograma={program};"
    query = db.select(sql)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return msg_error
    return jsonify(_format(query))


@Student.route('/program/<int:program>/<int:period>')
@jwt_required()
def get_period_program(program, period):
    sql = f'SELECT * FROM {table} WHERE REGISTRO={
        period} and idprograma={program}'
    query = db.select(sql)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return msg_error
    return jsonify(_format(query))


@Student.route('/documento/<documento>')
@jwt_required()
def get_documento(documento):
    sql = f"SELECT * FROM {table} WHERE documento='{documento}';"
    query = db.select(sql)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return msg_error
    return jsonify(_format(query))


@Student.route('/periods')
@jwt_required()
def get_periods():
    # Obtener datos desde la bd SQL server
    sql = f'SELECT DISTINCT REGISTRO FROM {table};'
    query = db.select(sql)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return msg_error
    periods_list = [int(p['REGISTRO']) for p in query]
    periods = sorted(periods_list)

    if not periods:
        return msg_error
    return jsonify(_format(periods))


@Student.route('/periods/program/<int:program>')
@jwt_required()
def get_periods_program(program):
    # Obtener datos desde la bd SQL server
    sql = f'SELECT DISTINCT REGISTRO FROM {table} WHERE idprograma={program};'
    query = db.select(sql)

    ex = exception(query)
    if ex:
        return ex

    if not query:
        return msg_error
    periods_list = [int(p.get('REGISTRO')) for p in query]
    periods = sorted(periods_list)

    if not periods:
        return msg_error

    return jsonify(_format(periods))


@Student.route('/programs')
@jwt_required()
def get_programs():
    # Obtener datos desde la bd SQL server
    sql = f'SELECT DISTINCT idprograma, program FROM {table};'
    query = db.select(sql)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return msg_error

    programs_df = pd.DataFrame(query).sort_values(
        by='program', ascending=True
    )
    programs_df['idprograma'] = programs_df['idprograma'].astype(int)
    programs = json.loads(programs_df.to_json(orient='records'))

    if not programs:
        return msg_error
    return jsonify(_format(programs))
