import logging
from flask import flash
from utils.constants import conditions


model_logger = logging.getLogger('model_logger')


############################################# VERIFICACION DE DATOS CONJUNTO #####################################################

def assign_types(data):
    # Asignar tipos de datos en cada column
    for key, value in conditions.items():
        mask = data[key].notna()
        data.loc[mask, key] = data.loc[mask, key].astype(value)
    return data


def verify_data(data, period_inicial, period_final, program):
    columns = list(conditions.keys())

    # Verificar si dataset tiene columns en str y la primera fila
    try:
        data.columns = map(str.lower, data.columns)
    except Exception as excep:
        model_logger.error(excep)
        return False, 'El dataset no tiene columns', None, period_inicial

    # Verificar si hay registros
    if not len(data) > 0:
        return False, 'El dataset no tiene registros (esta vacio)', None, period_inicial

    # Verificar Si todas las columns existen
    if not all(col in data.columns for col in columns):
        return False, 'El dataset ingresado no posee las columns requeridas', None, period_inicial

    if not len(data.columns) == len(columns):
        msg = 'El dataset ingresado tiene mas columns de las requeridas'
        return False, msg, None, period_inicial

    # Verificar si los tipos de datos de colunma son correctos
    try:
        data_verificada = assign_types(data)
    except Exception as excep:
        model_logger.error(excep)
        msg = 'El dataset ingresado no tiene los tipos de dato por column requeridos'
        return False, msg, None, period_inicial

    # Verificar si en dataset posee mas de un  valor en la column program
    if not len(dataset(data_verificada['program'].tolist())) == 1:
        msg = 'El dataset tiene resgistros de mas de un program, los models se ejecutan por program'
        return False, msg, None, period_inicial

    # Verificar si en dataset posee los valores de periodo Inicial y Final Correctamente
    if not data_verificada['registro'].max() == period_final:
        msg = f'El dataset no tiene como periodo final {
            period_final}, verifique los registros'
        return False, msg, None, period_inicial

    if not data_verificada['registro'].min() == period_inicial:
        _period_inicial = period_inicial
        period_inicial = data_verificada['registro'].min()
        msg = f'El dataset no tiene como periodo inicial {
            _period_inicial}, se reasignó a <b>{period_inicial}</b>'
        flash(msg, 'warning')

    if not (data_verificada['idprograma'] == program).all():
        msg = 'El dataset no pertenece al program indicado, verifique los registros'
        return False, msg, None, period_inicial

    # Verificacion correcta
    return True, None, data_verificada, period_inicial
