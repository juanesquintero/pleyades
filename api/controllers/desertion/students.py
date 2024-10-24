import json
import pandas as pd
from flask_jwt_extended import jwt_required
from flask import request, jsonify, Blueprint

from db.ies.db import DB
from utils.utils import exception, _format
from controllers.programs import exists as exists_program

Student = Blueprint('Student', __name__)

db = DB.getInstance()

tabla = 'VWDATADESERCION'

msg_error = {'msg': 'No hay concidencias'}, 404

##########################################################  VWDATADESERCION ##########################################################


@Student.route('/set/<int:programa>/<int:periodoInicio>/<int:periodoFin>')
@jwt_required()
def get_set_estudiantes(programa, periodoInicio, periodoFin):
    sql = f'SELECT * FROM {tabla} WHERE idprograma={programa} AND REGISTRO >= {
        periodoInicio} AND REGISTRO <= {periodoFin} ORDER BY REGISTRO;'
    query = db.select(sql)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return msg_error
    return jsonify(_format(query))


@Student.route('/periodo/<int:periodo>')
@jwt_required()
def get_period(periodo):
    sql = f'SELECT * FROM {tabla} WHERE REGISTRO={periodo};'
    query = db.select(sql)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return msg_error
    return jsonify(_format(query))


@Student.route('/programa/<int:programa>')
@jwt_required()
def get_program(programa):
    sql = f"SELECT * FROM {tabla} WHERE idprograma={programa};"
    query = db.select(sql)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return msg_error
    return jsonify(_format(query))


@Student.route('/programa/<int:programa>/<int:periodo>')
@jwt_required()
def get_period_program(programa, periodo):
    sql = f'SELECT * FROM {tabla} WHERE REGISTRO={
        periodo} and idprograma={programa}'
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
    sql = f"SELECT * FROM {tabla} WHERE documento='{documento}';"
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
    sql = f'SELECT DISTINCT REGISTRO FROM {tabla};'
    query = db.select(sql)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return msg_error
    periodos_list = [int(p['REGISTRO']) for p in query]
    periods = sorted(periodos_list)

    if not periods:
        return msg_error
    return jsonify(_format(periods))


@Student.route('/periods/programa/<int:programa>')
@jwt_required()
def get_periods_program(programa):
    # Obtener datos desde la bd SQL server
    sql = f'SELECT DISTINCT REGISTRO FROM {tabla} WHERE idprograma={programa};'
    query = db.select(sql)

    ex = exception(query)
    if ex:
        return ex

    if not query:
        return msg_error
    periodos_list = [int(p.get('REGISTRO')) for p in query]
    periods = sorted(periodos_list)

    if not periods:
        return msg_error

    return jsonify(_format(periods))


@Student.route('/programs')
@jwt_required()
def get_programs():
    # Obtener datos desde la bd SQL server
    sql = f'SELECT DISTINCT idprograma, programa FROM {tabla};'
    query = db.select(sql)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return msg_error

    programs_df = pd.DataFrame(query).sort_values(
        by='programa', ascending=True
    )
    programs_df['idprograma'] = programs_df['idprograma'].astype(int)
    programs = json.loads(programs_df.to_json(orient='records'))

    if not programs:
        return msg_error
    return jsonify(_format(programs))
