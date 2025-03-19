from flask import request, jsonify, Blueprint
from api.app.db.ies import DB
from flask_jwt_extended import jwt_required
from app.utils.utils import exception, _format
import pandas as pd
from app.schemas.result_schema import validate_post_schema
# Relaciones
from app.controllers.programs import exists as exists_program


Result = Blueprint('Result', __name__)

db = DB.getInstance()
table = 'TBLDES_RESULTADO_PREDICCION'
msg_error = {'msg': 'Can Not puedo completar the operación'}, 500
msg_exito = {'msg': 'Operación completada con exito!'}, 200

##########################################################  TBLDES_RESULTADO_PREDICCION ##########################################################


@Result.route('/ultimo/<program>/<int:semestre>', methods=['PUT'])
@jwt_required()
def put_ultimo(semestre, program):
    sql = f'UPDATE {table} SET blnultimo=0 WHERE semestre_prediccion={
        semestre} AND idprograma={program};'
    result = db.execute(sql)
    ex = exception(result)
    if ex:
        return ex
    if not (result):
        return msg_error
    return msg_exito


@Result.route('', methods=['POST'])
@jwt_required()
def post_insert_results():
    body = request.get_json()
    if not body or not validate_post_schema(body):
        return {'error': 'invalid body content'}, 400
    data = pd.DataFrame(body)
    data = data[
        [
            'documento', 'name_completo', 'idprograma',
            'prediccion', 'desertor', 'semestre_prediccion'
        ]
    ]
    result = db.multi_insert(data, table)
    ex = exception(result)
    if ex:
        return ex
    if not result:
        return msg_error
    return msg_exito
