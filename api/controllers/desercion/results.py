from flask import request, jsonify, Blueprint
from db.ies.db import DB
from flask_jwt_extended import jwt_required
from utils.utils import exception, _format
import pandas as pd
from schemas.resultado_schema import validate_post_schema
# Relaciones
from controllers.Programas import exists as exists_programa


Result = Blueprint('Result', __name__)

db = DB.getInstance()
tabla = 'TBLDES_RESULTADO_PREDICCION'
msg_error = {'msg': 'No se puedo completar la operación'}, 500
msg_exito = {'msg': 'Operación completada con exito!'}, 200

##########################################################  TBLDES_RESULTADO_PREDICCION ##########################################################


@Result.route('/ultimo/<programa>/<int:semestre>', methods=['PUT'])
@jwt_required()
def put_ultimo(semestre, programa):
    sql = f'UPDATE {tabla} SET blnultimo=0 WHERE semestre_prediccion={
        semestre} AND idprograma={programa};'
    result = db.execute(sql)
    ex = exception(result)
    if ex:
        return ex
    if not (result):
        return msg_error
    return msg_exito


@Result.route('', methods=['POST'])
@jwt_required()
def post_insertar_resultados():
    body = request.get_json()
    if not body or not validate_post_schema(body):
        return {'error': 'body invalido'}, 400
    data = pd.DataFrame(body)
    data = data[
        [
            'documento', 'nombre_completo', 'idprograma',
            'prediccion', 'desertor', 'semestre_prediccion'
        ]
    ]
    result = db.multi_insert(data, tabla)
    ex = exception(result)
    if ex:
        return ex
    if not result:
        return msg_error
    return msg_exito
