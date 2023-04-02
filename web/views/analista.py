import os
import pandas as pd
from dotenv import load_dotenv
from flask import request, session, Blueprint, render_template, send_file, redirect, url_for
from views.auth import login_required
from services.API import get
from utils.mixins import *

load_dotenv()

endopoint = 'resultados/'

Analista = Blueprint('Analista', __name__)

upload_folder = os.getcwd()+'/uploads'


@Analista.route('/modelos', methods=['GET'])
@login_required
def modelos():
    return render_template('analista/modelos/listar.html', conjuntos=[])


@Analista.route('/modelos/entrenar', methods=['GET'])
@login_required
def crear_entrenamiento():
    return render_template('analista/modelos/crear.html')


@Analista.route('/modelos/entrenar', methods=['POST'])
def entrenar():
    return render_template('analista/modelos/crear.html')


@Analista.route('/entrenamientos', methods=['GET'])
@login_required
def entrenamientos():
    return redirect(url_for('Analista.preparaciones'))


@Analista.route('/predicciones', methods=['GET'])
@login_required
def predicciones():
    return redirect(url_for('Analista.ejecuciones'))
