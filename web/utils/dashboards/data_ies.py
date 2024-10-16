import logging
import pandas as pd
from services.API import get

ies_route = 'desercion/institucion/'
students_route = 'desercion/estudiantes/'
error_logger = logging.getLogger('error_logger')


########################################################## Vista VWDATADESERCIONINSTITUCION de institucion ##########################################################

def get_IES_total_data(periodo: int):
    status, body = get(ies_route+'totales/{}'.format(periodo))
    return validate(status, body, True)


def get_IES_period(periodo: int):
    status, body = get(ies_route+'{}'.format(periodo))
    return validate(status, body, True)


def get_IES_programa(programa: int):
    status, body = get(ies_route+'programa/{}'.format(programa))
    return validate(status, body, True)


def get_IES_period_programa(periodo: int, programa: int):
    status, body = get(ies_route+'programa/{}/{}'.format(programa, periodo))
    return validate(status, body, True)


def check_IES_period_programa(periodo: int, programa: int):
    status, body = get(ies_route+'programa/{}/{}'.format(programa, periodo))
    return status


def get_periods():
    status, body = get(ies_route+'periods')
    return validate(status, body)


def get_programas():
    status, body = get(ies_route+'programs')
    return validate(status, body)


def get_programas_by_period(periodo: int):
    status, body = get(ies_route+'programs/{}'.format(periodo))
    return validate(status, body)


def get_programa(programa: int):
    status, body = get(ies_route+'programa/{}'.format(programa))
    return validate(status, body, True)

########################################################### Vista VWDATADESERCION de estudiantes ##########################################################


def get_students_period_programa(periodo: int, programa: int):
    status, body = get(f'{students_route}programa/{programa}/{periodo}')
    return validate(status, body, True)


def get_students_programa(programa: str):
    status, body = get(f'{students_route}programa/{programa}')
    return validate(status, body, True)


def get_students_documento(documento: str):
    status, body = get(f'{students_route}documento/{documento}')
    return validate(status, body, True)


def get_periods_origen():
    status, body = get(students_route+'periods')
    return validate(status, body)


def get_programas_origen():
    status, body = get(students_route+'programs')
    return validate(status, body)


def validate(status, body, df=False):
    if status:
        if df:
            return pd.DataFrame(body)
        return body
    raise Exception('Consulta fallida a la base de datos de Deserción')
