import logging
import pandas as pd
from flask import flash
from utils.constants import col_preparadas
from .model import load_classifer
from .preparation import elimination_predict

model_logger = logging.getLogger('model_logger')


def predict(data_a_predecir, period_a_predecir, basic_info):

    data_a_predecir['registro'] = data_a_predecir['registro'].astype(int)

    if len(data_a_predecir) < 3:
        raise Exception(
            f'Hay muy pocos registros para el periodo {
                period_a_predecir} (menos de 3)', True
        )

    # Eliminacion depuracion de columnas
    data_a_predecir = elimination_predict(data_a_predecir)

    # Obtener el clasificador como archivo local
    nombre_modelo = basic_info.get('modelo')
    mejor_clasificador = load_classifer(nombre_modelo)

    # Predecir
    result = predict_classifier(
        data_a_predecir, period_a_predecir, mejor_clasificador
    )

    results = {
        **basic_info,
        'tipo': 'Prediccion',
        'desertores': result.get('desertores'),
        'period_a_predecir': int(period_a_predecir),
        'students_analizados': result.get('total_analizados'),
        'desercion_prevista': result.get('desercion'),
        'potenciales_desertores': result.get('total'),
        'clasificador': str(mejor_clasificador.__class__.__name__),
    }

    return results, result.get('resultado')


def calculate_desercion(total_estudiantes, potenciales_desertores):
    total_desertores = len(potenciales_desertores.index)
    desercion_prevista = int(total_desertores) / \
        int(total_estudiantes)

    return total_desertores, desercion_prevista


def predict_classifier(data_a_predecir, period_a_predecir, mejor_clasificador):
    predc_sem_act = data_a_predecir[
        [
            'registro', 'semestre', 'documento', 'nombre_completo',
            'desertor', 'idprograma', 'idestado', 'promedio_acumulado'
        ]
    ]

    if data_a_predecir.empty:
        raise Exception(
            'No estudiantes para predecir en ese conjunto!', True
        )

    try:
        predc_sem_act['prediccion'] = mejor_clasificador.predict(
            data_a_predecir[col_preparadas]
        )
    except Exception as excep:
        model_logger.error(excep)
        flash('Por favor intente con otro periodo o programa', 'warning')
        raise Exception('<b>Ocurrió un error al ejecutar la predicción!</b>')
    total_students_analizados = len(predc_sem_act['documento'].unique())
    potenciales_desertores = predc_sem_act.query('prediccion == 1 & desertor == 0').drop_duplicates(
        subset=['documento'],
        keep='first'
    ).reset_index()

    # TODO filtro de idestado
    # Elminar no matriculados
    potenciales_desertores = potenciales_desertores.query(
        f"idestado == 6 & registro == {period_a_predecir}"
    )

    potenciales_desertores = potenciales_desertores.drop('registro', axis=1)

    # Re asignar tipos
    potenciales_desertores['semestre'] = potenciales_desertores['semestre'].astype(
        int, copy=False
    )
    potenciales_desertores['documento'] = potenciales_desertores['documento'].astype(
        str, copy=False
    )

    # Setear results para insertar en la BD
    potenciales_desertores['semestre_prediccion'] = period_a_predecir

    # Filtar desertores si desercio alta
    potenciales_desertores, total_desertores, desercion_prevista = filter_high_desertion(
        potenciales_desertores,
        total_students_analizados
    )

    resultados_desertores = potenciales_desertores

    ''' FASE 3 '''
    pd.crosstab(predc_sem_act.prediccion, predc_sem_act.desertor, margins=True)

    # matriz_confusion = pd.crosstab(
    #     predc_sem_act.prediccion, predc_sem_act.desertor, margins=True
    # )

    potenciales_desertores.drop(['index'], axis=1, inplace=True)

    # Reasignar el tipo de la columna documento
    resultados_desertores['documento'] = resultados_desertores['documento'].astype(
        str, copy=False)
    resultados_desertores = resultados_desertores[[
        'documento',
        'nombre_completo',
        'desertor',
        'prediccion',
        'semestre_prediccion',
        'idprograma'
    ]]

    return {
        'resultado': resultados_desertores,
        'desertores': potenciales_desertores,
        'total': int(total_desertores),
        'total_analizados': int(total_students_analizados),
        'desercion': float(round(desercion_prevista, 3))
    }


def filter_high_desertion(desertores, total_estudiantes):
    low_average = 3.5
    level = 1
    total_desertores, desercion_prevista = calculate_desercion(
        total_estudiantes, desertores
    )

    while desercion_prevista > 0.19:
        # Elminar desercíon temprana
        if level < 2:
            no_desercion_temprana = desertores.query(
                f'semestre > {level} & promedio_acumulado > 0.4'
            )
            if not no_desercion_temprana.empty:
                desertores = no_desercion_temprana

                total_desertores, desercion_prevista = calculate_desercion(
                    total_estudiantes, desertores
                )

        # Filtrar bajo promedio por alta deserción
        _desertores = desertores.query(
            f'promedio_acumulado < {low_average}'
        )
        _total_desertores, _desercion_prevista = calculate_desercion(
            total_estudiantes, _desertores
        )

        if _desercion_prevista > 0:
            desertores, total_desertores, desercion_prevista = _desertores, _total_desertores, _desercion_prevista
            low_average -= 0.05
            level += 1
        else:
            continue

    return desertores, total_desertores, desercion_prevista
