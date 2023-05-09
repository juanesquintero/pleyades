# Algoritmos comunes para clasificación
# Apoyo para la validación cruzada
from sklearn import svm, tree, linear_model, neighbors, naive_bayes, ensemble, discriminant_analysis

# Algoritmos de Machine Learning (AML)
AML = [
    # Métodos Combinados
    ensemble.AdaBoostClassifier(),
    ensemble.BaggingClassifier(),
    ensemble.ExtraTreesClassifier(),
    ensemble.GradientBoostingClassifier(),
    ensemble.RandomForestClassifier(),

    # Modelo Lineal Generalizado (GLM)
    linear_model.LogisticRegressionCV(),
    linear_model.PassiveAggressiveClassifier(),
    linear_model.RidgeClassifierCV(),
    linear_model.SGDClassifier(),
    linear_model.Perceptron(),

    # Navies Bayes
    naive_bayes.BernoulliNB(),
    naive_bayes.GaussianNB(),

    # K-Nearest Neighbor
    neighbors.KNeighborsClassifier(),

    # Máquina de Vectores de Soporte (SVM)
    svm.SVC(probability=True),
    svm.LinearSVC(),

    # Árboles de Decisión
    tree.DecisionTreeClassifier(),
    tree.ExtraTreeClassifier(),

    # Análisis Discriminante (Discriminant Analysis)
    discriminant_analysis.LinearDiscriminantAnalysis(),
    discriminant_analysis.QuadraticDiscriminantAnalysis(),
]

colores = [
    'rgb(30, 75, 131)',
    'rgb(25, 95, 201)',
    'rgb(186, 41, 41)',
    'rgb(30, 59, 87)',
    'rgb(85, 128, 168)',
    'rgb(0, 27, 53)',
    'rgb(184, 210, 235)',
    'rgb(88, 173, 199)'
]

columnas_eliminar_1_anteriores = [
    'registro',
    'nombre_completo',
    'tipo_documento',
    'documento',
    'jornada',
    'lugar_residencia_sede',
    'trabaja',
    'puntaje_icfes',
    'beca',
    'periodo_ingreso',
    'ultimo_periodo',
    'biologia',
    'ciencias_naturales',
    'ciencias_sociales',
    'competencias_ciudadanas',
    'filosofia',
    'fisica',
    'geografia',
    'historia',
    'ingles',
    'lectura_critica',
    'lenguaje',
    'matematicas',
    'quimica',
    'razonamiento_cuantitativo',
    'sociales_y_ciudadanas',
    'promedio_semestre',
    'programa',
    'tipo_programa',
    'idfacultad',
    'facultad',
    'idmatricula',
    'idaspiracion',
    'idprograma'
]

columnas_eliminar_1 = [
    'registro',
    'nombre_completo',
    'tipo_documento',
    'documento',
    'jornada',
    'lugar_residencia_sede',
    'trabaja',
    'puntaje_icfes',
    'beca',
    'periodo_ingreso',
    'ultimo_periodo',
    'biologia',
    'ciencias_naturales',
    'ciencias_sociales',
    'competencias_ciudadanas',
    'filosofia',
    'fisica',
    'geografia',
    'historia',
    'ingles',
    'lectura_critica',
    'lenguaje',
    'matematicas',
    'quimica',
    'razonamiento_cuantitativo',
    'sociales_y_ciudadanas',
    'promedio_semestre',
    'programa',
    'tipo_programa',
    'idfacultad',
    'facultad',
    'estrato_residencia',
    'celular_telefono',
    'fecha_nacimiento',
    'sanciones_multas',
    'participacion_semillero_investigacion',
    'correo_electronico',
    'dtfecharegistro',
    'idmatricula',
    'idaspiracion',
    'idprograma',
    'idestado '
]

columnas_eliminar_nulos = [
    'semestre', 'genero', 'estado_civil', 'etnia', 'victima',
    'pertenece_grupo_vulnerable', 'promedio_acumulado', 'creditos_programa',
    'creditos_aprobados_sem', 'creditos_aprobados_acum', 'creditos_reprobados_sem', 'creditos_reprobados_acum',
    'creditos_cancelados_sem', 'creditos_cancelados_acum', 'creditos_matriculados_sem', 'intersemestral', 'creditos_matriculados_acum'
]

columnas_eliminar_2_anteriores = [
    'asignaturas_aprobadas_acum', 'asignaturas_reprobadas_acum'
]
columnas_eliminar_2 = [
    'asignaturas_aprobadas_acum', 'asignaturas_reprobadas_acum',
    'asignaturas_programa', 'asignaturas_canceladas_sem', 'asignaturas_canceladas_acum',
]

col_preparadas = ['semestre', 'edad', 'genero', 'estado_civil', 'etnia', 'victima',
                  'pertenece_grupo_vulnerable', 'creditos_programa',  'creditos_aprobados_sem', 'creditos_aprobados_acum',
                  'asignaturas_aprobadas_sem', 'creditos_reprobados_sem', 'creditos_reprobados_acum', 'asignaturas_reprobadas_sem',
                  'creditos_cancelados_sem', 'creditos_cancelados_acum', 'creditos_matriculados_sem', 'creditos_matriculados_acum',
                  'promedio_acumulado', 'intersemestral'
                  ]

condiciones = {
    'registro':                                 int,
    'semestre':                                 int,
    'jornada':                                  str,
    'nombre_completo':                          str,
    'tipo_documento':                           str,
    'documento':                                str,
    'edad':                                     int,
    'genero':                                   str,
    'estado_civil':                             str,
    'lugar_residencia_sede':                    str,
    'trabaja':                                  str,
    'etnia':                                    str,
    'victima':                                  str,
    'pertenece_grupo_vulnerable':               str,
    'creditos_programa':                        int,
    'creditos_aprobados_sem':                   int,
    'creditos_aprobados_acum':                  int,
    'asignaturas_aprobadas_sem':                int,
    'asignaturas_aprobadas_acum':               int,
    'creditos_reprobados_sem':                  int,
    'creditos_reprobados_acum':                 int,
    'asignaturas_reprobadas_sem':               int,
    'asignaturas_reprobadas_acum':              int,
    'creditos_cancelados_sem':                  int,
    'creditos_cancelados_acum':                 int,
    'creditos_matriculados_sem':                int,
    'creditos_matriculados_acum':               int,
    'promedio_semestre':                        float,
    'promedio_acumulado':                       float,
    'puntaje_icfes':                            float,
    'beca':                                     str,
    'intersemestral':                           str,
    'desertor':                                 str,
    'periodo_ingreso':                          int,
    'ultimo_periodo':                           int,
    'biologia':                                 float,
    'ciencias_naturales':                       float,
    'ciencias_sociales':                        float,
    'competencias_ciudadanas':                  float,
    'filosofia':                                float,
    'fisica':                                   float,
    'geografia':                                float,
    'historia':                                 float,
    'ingles':                                   float,
    'lectura_critica':                          float,
    'lenguaje':                                 float,
    'matematicas':                              float,
    'quimica':                                  float,
    'razonamiento_cuantitativo':                float,
    'sociales_y_ciudadanas':                    float,
    'idmatricula':                              int,
    'idaspiracion':                             int,
    'idprograma':                               int,
    'programa':                                 str,
    'tipo_programa':                            str,
    'idfacultad':                               int,
    'facultad':                                 str,
    'estrato_residencia':                       str,
    'celular_telefono':                         str,
    'fecha_nacimiento':                         str,
    'sanciones_multas':                         str,
    'participacion_semillero_investigacion':    str,
    'correo_electronico':                       str,
    'asignaturas_programa':                     int,
    'asignaturas_canceladas_sem':               int,
    'asignaturas_canceladas_acum':              int,
    'dtfecharegistro':                          str,
    'idestado':                                 int
}
