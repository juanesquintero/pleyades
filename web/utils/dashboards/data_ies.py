import logging
import pandas as pd
from services.API import get

ies_route = 'desertion/institute/'
students_route = 'desertion/students/'
error_logger = logging.getLogger('error_logger')


########################################################## Vista VWDATADESERCIONINSTITUCION de institute ##########################################################

def get_IES_total_data(periodo: int):
    status, body = get(ies_route+'totales/{}'.format(periodo))
    return validate(status, body, True)


def get_IES_period(periodo: int):
    status, body = get(ies_route+'{}'.format(periodo))
    return validate(status, body, True)


def get_IES_program(programa: int):
    status, body = get(ies_route+'programa/{}'.format(programa))
    return validate(status, body, True)


def get_IES_period_program(periodo: int, programa: int):
    status, body = get(ies_route+'programa/{}/{}'.format(programa, periodo))
    return validate(status, body, True)


def check_IES_period_program(periodo: int, programa: int):
    status, body = get(ies_route+'programa/{}/{}'.format(programa, periodo))
    return status


def get_periods():
    status, body = get(ies_route+'periods')
    return validate(status, body)


def get_programs():
    status, body = get(ies_route+'programs')
    return validate(status, body)


def get_programs_by_period(periodo: int):
    status, body = get(ies_route+'programs/{}'.format(periodo))
    return validate(status, body)


def get_program(programa: int):
    status, body = get(ies_route+'programa/{}'.format(programa))
    return validate(status, body, True)

########################################################### Vista VWDATADESERCION de students ##########################################################


def get_students_period_program(periodo: int, programa: int):
    status, body = get(f'{students_route}programa/{programa}/{periodo}')
    return validate(status, body, True)


def get_students_program(programa: str):
    status, body = get(f'{students_route}programa/{programa}')
    return validate(status, body, True)


def get_students_documento(documento: str):
    status, body = get(f'{students_route}documento/{documento}')
    return validate(status, body, True)


def get_periods_origen():
    status, body = get(students_route+'periods')
    return validate(status, body)


def get_programs_origen():
    status, body = get(students_route+'programs')
    return validate(status, body)


def validate(status, body, df=False):
    if status:
        if df:
            return pd.DataFrame(body)
        return body
    raise Exception('Consulta fallida a la base de datos de Deserción')
