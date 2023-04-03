import os
import pandas as pd
import utils.tableros.data_ies as DataIES
from dotenv import load_dotenv
from flask import request, session, Blueprint, render_template, send_file, redirect, url_for, jsonify
from views.auth import login_required
from services.API import get
import views.conjuntos as conjuntos
from utils.mixins import *

load_dotenv()

endopoint = 'analista/modelos/'

Analista = Blueprint('Analista', __name__)

modelos_folder = os.getcwd()+'/uploads/modelos'


@Analista.route('/modelos', methods=['GET'])
@login_required
def modelos():
    return render_template('analista/modelos/listar.html', modelos=[{
        'nombre': 'Modelo 1',
        'programa': 'Ing Sistemas',
        'tipo': 'SKLear Algorithm',
    }])


@Analista.route('/modelos/descargar', methods=['POST'])
@login_required
def descargar():
    modelo = dict(request.values).get('nombre')
    ruta = f'{modelos_folder}/{modelo}.pkl'

    if os.path.exists(ruta):
        return send_file(ruta, as_attachment=True)

    return render_template('utils/mensaje.html', mensaje='No se encontro el archivo a descargar')


@Analista.route('/modelos/entrenar', methods=['GET', 'POST'])
@login_required
def entrenar():
    if request.method == 'GET':
        return formulario_entrenar()
    conjunto = dict(request.values)
    return conjuntos.guardar(conjunto)
    

@Analista.route('/modelos/periodos/<int:programa>')
@login_required
def get_periodos_programa(programa):
    status, body = get(f'desercion/estudiantes/periodos/programa/{programa}')
    if status:
        return jsonify(body)
    return jsonify([])


@Analista.route('/modelos/predecir', methods=['POST'])
def predecir():
    return render_template(endopoint+'crear.html')


@Analista.route('/entrenamientos', methods=['GET'])
@login_required
def entrenamientos():
    return redirect(url_for('Resultado.preparaciones'))


@Analista.route('/predicciones', methods=['GET'])
@login_required
def predicciones():
    return redirect(url_for('Resultado.ejecuciones'))


def formulario_entrenar():
    periodos = DataIES.get_periodos_origen()
    status_f, body_f = get('facultades')
    status_p, body_p = get('programas')

    if status_f and status_p and periodos:
        return render_template(endopoint+'crear.html', facultades=body_f, programas=body_p)
    
    if not status_f and not status_p:
        error = {**body_f, **body_p}
    elif not status_f:
        error = body_f
    else:
        error = body_p
    return render_template('utils/mensaje.html', mensaje='No se pudieron cargar las programas y las facultades', submensaje=error)
