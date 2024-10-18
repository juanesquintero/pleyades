import logging
from flask import flash
from utils.constants import condiciones


model_logger = logging.getLogger('model_logger')


############################################# VERIFICACION DE DATOS CONJUNTO #####################################################

def assign_types(data):
    # Asignar tipos de datos en cada columna
    for key, value in condiciones.items():
        mask = data[key].notna()
        data.loc[mask, key] = data.loc[mask, key].astype(value)
    return data


def verify_data(data, period_inicial, period_final, programa):
    columnas = list(condiciones.keys())

    # Verificar si conjunto tiene columnas en str y la primera fila
    try:
        data.columns = map(str.lower, data.columns)
    except Exception as excep:
        model_logger.error(excep)
        return False, 'El conjunto no tiene columnas', None, period_inicial

    # Verificar si hay registros
    if not len(data) > 0:
        return False, 'El conjunto no tiene registros (esta vacio)', None, period_inicial

    # Verificar Si todas las columnas existen
    if not all(col in data.columns for col in columnas):
        return False, 'El conjunto ingresado no posee las columnas requeridas', None, period_inicial

    if not len(data.columns) == len(columnas):
        msg = 'El conjunto ingresado tiene mas columnas de las requeridas'
        return False, msg, None, period_inicial

    # Verificar si los tipos de datos de colunma son correctos
    try:
        data_verificada = assign_types(data)
    except Exception as excep:
        model_logger.error(excep)
        msg = 'El conjunto ingresado no tiene los tipos de dato por columna requeridos'
        return False, msg, None, period_inicial

    # Verificar si en conjunto posee mas de un  valor en la columna programa
    if not len(set(data_verificada['programa'].tolist())) == 1:
        msg = 'El conjunto tiene resgistros de mas de un programa, los modelos se ejecutan por programa'
        return False, msg, None, period_inicial

    # Verificar si en conjunto posee los valores de periodo Inicial y Final Correctamente
    if not data_verificada['registro'].max() == period_final:
        msg = f'El conjunto no tiene como periodo final {
            period_final}, verifique los registros'
        return False, msg, None, period_inicial

    if not data_verificada['registro'].min() == period_inicial:
        _period_inicial = period_inicial
        period_inicial = data_verificada['registro'].min()
        msg = f'El conjunto no tiene como periodo inicial {
            _period_inicial}, se reasignó a <b>{period_inicial}</b>'
        flash(msg, 'warning')

    if not (data_verificada['idprograma'] == programa).all():
        msg = 'El conjunto no pertenece al programa indicado, verifique los registros'
        return False, msg, None, period_inicial

    # Verificacion correcta
    return True, None, data_verificada, period_inicial
