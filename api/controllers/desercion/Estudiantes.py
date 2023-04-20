import json
import pandas as pd
from flask_jwt_extended import jwt_required
from flask import request, jsonify, Blueprint

from db.ies.db import DB
from utils.utils import exception, _format
from controllers.Programas import exists as exists_programa

Estudiante = Blueprint('Estudiante', __name__)

db = DB.getInstance()

tabla = 'VWDATADESERCION'

msg_error = {'msg': 'No hay concidencias'}, 404

##########################################################  VWDATADESERCION ##########################################################


@Estudiante.route('/conjunto/<int:programa>/<int:periodoInicio>/<int:periodoFin>')
@jwt_required()
def get_conjunto_estudiantes(programa, periodoInicio, periodoFin):
    sql = f'SELECT * FROM {tabla} WHERE idprograma={programa} AND REGISTRO >= {periodoInicio} AND REGISTRO <= {periodoFin} ORDER BY REGISTRO;'
    query = db.select(sql)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return msg_error
    return jsonify(_format(query))


@Estudiante.route('/periodo/<int:periodo>')
@jwt_required()
def get_periodo(periodo):
    sql = f'SELECT * FROM {tabla} WHERE REGISTRO={periodo};'
    query = db.select(sql)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return msg_error
    return jsonify(_format(query))


@Estudiante.route('/programa/<int:programa>')
@jwt_required()
def get_programa(programa):
    sql = f"SELECT * FROM {tabla} WHERE idprograma={programa};"
    query = db.select(sql)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return msg_error
    return jsonify(_format(query))


@Estudiante.route('/programa/<int:programa>/<int:periodo>')
@jwt_required()
def get_periodo_programa(programa, periodo):
    sql = f'SELECT * FROM {tabla} WHERE REGISTRO={periodo} and idprograma={programa}'
    query = db.select(sql)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return msg_error
    return jsonify(_format(query))


@Estudiante.route('/documento/<documento>')
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


@Estudiante.route('/periodos')
@jwt_required()
def get_periodos():
    # Obtener datos desde la bd SQL server
    sql = f'SELECT DISTINCT REGISTRO FROM {tabla};'
    query = db.select(sql)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return msg_error
    periodos_list = [int(p['REGISTRO']) for p in query]
    periodos = sorted(periodos_list)

    if not periodos:
        return msg_error
    return jsonify(_format(periodos))


@Estudiante.route('/periodos/programa/<int:programa>')
@jwt_required()
def get_periodos_programa(programa):
    # Obtener datos desde la bd SQL server
    sql = f'SELECT DISTINCT REGISTRO FROM {tabla} WHERE idprograma={programa};'
    query = db.select(sql)

    ex = exception(query)
    if ex:
        return ex

    if not query:
        return msg_error
    periodos_list = [int(p.get('REGISTRO')) for p in query]
    periodos = sorted(periodos_list)

    if not periodos:
        return msg_error

    return jsonify(_format(periodos))


@Estudiante.route('/programas')
@jwt_required()
def get_programas():
    # Obtener datos desde la bd SQL server
    sql = f'SELECT DISTINCT idprograma, programa FROM {tabla};'
    query = db.select(sql)
    ex = exception(query)
    if ex:
        return ex
    if not query:
        return msg_error

    programas_df = pd.DataFrame(query).sort_values(
        by='programa', ascending=True
    )
    programas_df['idprograma'] = programas_df['idprograma'].astype(int)
    programas = json.loads(programas_df.to_json(orient='records'))

    if not programas:
        return msg_error
    return jsonify(_format(programas))
