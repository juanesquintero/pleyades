import pandas as pd
from sklearn import model_selection
from utils.constants import AML, col_preparadas
from .preparation import elimination
from .prediction import predict_classifier
from .model import save_classifirer


def execute_model(data, conjunto, no_desertion=False):
    initial_data = data
    data['registro'] = data['registro'].astype(int)

    basic_info = {
        'idprograma': int(data['idprograma'][0]),
        'programa': str(data['programa'][0]),
        'idfacultad': int(data['idfacultad'][0]),
        'faculty': str(data['faculty'][0]),
        'tipo': 'Entrenamiento',
    }

    # Eliminacion depuracion de columnas
    data, data_a_predecir, period_a_predecir = elimination(data, no_desertion)

    basic_info['period_a_predecir_mas_1'] = f'{period_a_predecir} + 1'

    if len(data_a_predecir) <= 0:
        return False, 'No hay suficientes datos en el periodo final, revisa el conjunto.'

    ''' FASE 1 '''

    cv_split = model_selection.ShuffleSplit(
        n_splits=10, test_size=.3, train_size=.7, random_state=42
    )
    AML_columns = [
        'Nombre',
        'objeto',
        'Parametros',
        'Precision Media de Prueba',
        'STD de la Precision * 3',
        'Tiempo'
    ]
    AML_compare = pd.DataFrame(columns=AML_columns)
    Target = ['desertor']
    AML_predict = data[Target]
    row_index = 0

    for alg in AML:
        try:
            AML_nombre = alg.__class__.__name__
            AML_compare.loc[row_index, 'Nombre'] = AML_nombre
            AML_compare.loc[row_index, 'Parametros'] = str(alg.get_params())
            cv_results = model_selection.cross_validate(
                alg,
                data[col_preparadas],
                data[Target],
                cv=cv_split
            )

            AML_compare.loc[
                row_index,
                'Precision Media de Prueba'
            ] = cv_results['test_score'].mean()
            # Si es una muestra aleatoria sin sesgo, entonces la media +/- 3*(desviación estándar), deberían capturar el 99.7% de los subsets
            AML_compare.loc[
                row_index,
                'STD de la Precision * 3'
            ] = cv_results['test_score'].std()*3
            AML_compare.loc[row_index,
                            'Tiempo'] = cv_results['fit_time'].mean()
            alg.fit(data[col_preparadas], data[Target])
            AML_predict[AML_nombre] = alg.predict(data[col_preparadas])
            AML_compare.loc[row_index, 'objeto'] = alg
            row_index += 1
        except:
            continue
    AML_compare.sort_values(
        by=['Precision Media de Prueba'],
        ascending=False,
        inplace=True
    )

    AML_best = AML_compare.head(1)
    mejor_clasificador = AML_best['objeto'].tolist()[0]

    # Usar mejor clasificador para prediction
    result = predict_classifier(
        data_a_predecir, period_a_predecir, mejor_clasificador
    )

    if not result.get('resultado').any().any() and not no_desertion:
        execute_model(initial_data, conjunto, True)

    # Guardar clasificador
    save_classifirer(mejor_clasificador, conjunto)

    precision_model = AML_best['Precision Media de Prueba'].tolist()[0] * 100

    results = {
        **basic_info,
        'clasificador': str(AML_best['Nombre'].tolist()[0]),
        'precision': float(round(precision_model, 2)),
        'period_anterior': int(period_a_predecir),
        'desertores': result.get('desertores'),
        'period_a_predecir': int(period_a_predecir),
        'students_analizados': result.get('total_analizados'),
        'desercion_prevista': result.get('desertion'),
        'desertores_reportados':  int(len(data_a_predecir.query(f'desertor == 1 & registro == {period_a_predecir}'))),
        'potenciales_desertores': result.get('total'),
    }

    return results, result.get('resultado')
