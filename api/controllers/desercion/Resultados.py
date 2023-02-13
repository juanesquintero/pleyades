from flask import request, jsonify, Blueprint
from db.cli.db_cli import DB
from flask_jwt_extended import jwt_required
from utils.utils import exception, _format
import pandas as pd
from schemas.resultadoSchema import validate_post_schema
# Relaciones
from controllers.Programas import exists as exists_programa


Resultado = Blueprint('Resultado', __name__)

db = DB.getInstance()
tabla = 'TBLDES_RESULTADO_PREDICCION'
msg_error = { 'msg': 'No se puedo completar la operación' }, 500
msg_exito = { 'msg': 'Operación completada con exito!' }, 200

##########################################################  TBLDES_RESULTADO_PREDICCION ##########################################################

@Resultado.route('/ultimo/<programa>/<int:semestre>', methods=['PUT'])
@jwt_required()
def put_ultimo(semestre, programa):
    sql = "UPDATE {} SET blnultimo=0 WHERE semestre_prediccion={} AND idprograma={};".format(tabla, semestre, programa)
    result = db.execute(sql)
    ex = exception(result)
    if ex: 
        return ex
    if not(result):  return msg_error
    return msg_exito

@Resultado.route('', methods=['POST'])
@jwt_required()
def post_insertar_resultados():
    body = request.get_json()
    if not(validate_post_schema(body)):
        return {'error': "body invalido"}, 400
    if not(body):  return msg_error
    data = pd.DataFrame(body)
    result = db.multi_insert(data, tabla)
    ex = exception(result)
    if ex: 
        return ex
    if not(result):  return msg_error
    return msg_exito
