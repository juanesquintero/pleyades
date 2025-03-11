import logging
import pandas as pd
from web.app.services.API import get

ies_route = 'desertion/institute/'
students_route = 'desertion/students/'
error_logger = logging.getLogger('error_logger')


########################################################## Vista VWDATADESERCIONINSTITUCION de institute ##########################################################

def get_ies_total_data(period: int):
    status, body = get(ies_route+'totals/{}'.format(period))
    return validate(status, body, True)


def get_ies_period(period: int):
    status, body = get(ies_route+'{}'.format(period))
    return validate(status, body, True)


def get_ies_program(program: int):
    status, body = get(ies_route+'program/{}'.format(program))
    return validate(status, body, True)


def get_ies_period_program(period: int, program: int):
    status, body = get(ies_route+'program/{}/{}'.format(program, period))
    return validate(status, body, True)


def check_ies_period_program(period: int, program: int):
    status, body = get(ies_route+'program/{}/{}'.format(program, period))
    return status


def get_periods():
    status, body = get(ies_route+'periods')
    return validate(status, body)


def get_programs():
    status, body = get(ies_route+'programs')
    return validate(status, body)


def get_programs_by_period(period: int):
    status, body = get(ies_route+'programs/{}'.format(period))
    return validate(status, body)


def get_program(program: int):
    status, body = get(ies_route+'program/{}'.format(program))
    return validate(status, body, True)

########################################################### Vista VWDATADESERCION de students ##########################################################


def get_students_period_program(period: int, program: int):
    status, body = get(f'{students_route}program/{program}/{period}')
    return validate(status, body, True)


def get_students_program(program: str):
    status, body = get(f'{students_route}program/{program}')
    return validate(status, body, True)


def get_students_documento(documento: str):
    status, body = get(f'{students_route}documento/{documento}')
    return validate(status, body, True)


def get_periods_origin():
    status, body = get(students_route+'periods')
    return validate(status, body)


def get_programs_origin():
    status, body = get(students_route+'programs')
    return validate(status, body)


def validate(status, body, df=False):
    if status:
        if df:
            return pd.DataFrame(body)
        return body
    raise Exception('Consulta fallida a the base de datos de Deserción')
