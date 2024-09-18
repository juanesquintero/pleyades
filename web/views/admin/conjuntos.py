import os
from flask import request, Blueprint, render_template, redirect, url_for
from dotenv import load_dotenv
from ast import literal_eval
from views.auth import only_admin
from services.API import get, put, delete

from utils.mixins import *

load_dotenv()

ConjuntoAdmin = Blueprint("ConjuntoAdmin", __name__)

endopoint = "conjuntos/"

upload_folder = os.getcwd() + "/uploads"


@ConjuntoAdmin.route("/")
@ConjuntoAdmin.route("/crudos")
@only_admin
def crudos():
    return get_list("crudos")


@ConjuntoAdmin.route("/enproceso")
@only_admin
def en_proceso():
    return get_list("en proceso")


@ConjuntoAdmin.route("/procesados")
@only_admin
def procesados():
    return get_list("procesados")


def get_list(estado: str):
    status_p, body_p = get("programas")
    status_c, body_c = get("conjuntos/estado/" + estado)
    if status_c and status_p:
        return render_template(
            "admin/" + endopoint + estado.replace(" ", "_") + ".html", conjuntos=body_c, programas=body_p
        )

    if not (status_c) and not (status_p):
        error = {**body_c, **body_p}
    elif not (status_c):
        error = body_c
    else:
        error = body_p
    return render_template(
        "admin/" + endopoint + estado.replace(" ", "_") + ".html",
        conjuntos=[],
        error=error,
    )


@ConjuntoAdmin.route("/editar", methods=["POST"])
@only_admin
def post_edit():
    body = dict(request.values)
    conjunto = literal_eval(body["conjunto"])
    status_p, body_p = get("programas")
    if status_p:
        return render_template(
            "admin/" + endopoint + "editar.html", c=conjunto, programas=body_p
        )
    else:
        return render_template(
            "utils/mensaje.html",
            mensaje="No se obtener los programas",
            submensaje=body_p,
        )


@ConjuntoAdmin.route("/actualizar", methods=["POST"])
@only_admin
def update():
    conjunto = dict(request.values)
    nombre = conjunto.pop("nombre")

    status, body = put("conjuntos/" + nombre, conjunto)
    if status:
        return redirect(url_for("ConjuntoAdmin.crudos"))

    return render_template(
        "utils/mensaje.html",
        mensaje="No se pudo actualizar la conjunto",
        submensaje=body,
    )


@ConjuntoAdmin.route("/borrar", methods=["POST"])
@only_admin
def delete():
    body = dict(request.values)
    conjunto = literal_eval(body["conjunto"])
    status_p, body_p = get("programas")
    if status_p:
        return render_template(
            "admin/" + endopoint + "borrar.html", c=conjunto, programas=body_p
        )
    else:
        return render_template(
            "utils/mensaje.html",
            mensaje="No se obtener los programas",
            submensaje=body_p,
        )


@ConjuntoAdmin.route("/eliminar", methods=["POST"])
@only_admin
def eliminar():
    conjunto = dict(request.values)
    nombre = conjunto.pop("nombre")
    status, body = delete("conjuntos/" + nombre)
    if status:
        # Eliminar archivos relacionados en el servidor
        exito, pagina_error = eliminar_archivo(
            upload_folder + "/crudos/" + "C " + nombre + ".xls"
        )
        if not (exito):
            return pagina_error
        if conjunto["estado"] == "Procesados":
            exito, pagina_error = eliminar_archivo(
                upload_folder + "/procesados/" + "P " + nombre + ".xls"
            )
            if not (exito):
                return pagina_error

        return redirect(url_for("ConjuntoAdmin.crudos"))
    else:
        return render_template(
            "utils/mensaje.html",
            mensaje="No se pudo Eliminar el conjunto",
            submensaje=body,
        )


@ConjuntoAdmin.route("/eliminar/todos", methods=["POST"])
@only_admin
def eliminar_todos():
    estado = dict(request.values).pop("estado")
    status, body = delete(f"conjuntos/todos/{estado}")

    if status:
        # Eliminar archivos relacionados en el servidor
        remove_all_files(f"{upload_folder}/{estado}")
        route = estado.replace(" ", "_")
        return redirect(url_for(f"ConjuntoAdmin.{route}"))

    return render_template(
        "utils/mensaje.html",
        mensaje="No se pudo Eliminar los conjuntos",
        submensaje=body,
    )


def remove_all_files(folder_path):
    file_to_keep = ".gitignore"
    # Iterate over all files in the folder
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            # Check if the file is not the one to keep
            if filename != file_to_keep:
                # Check if the path is a file (not a directory)
                if os.path.isfile(file_path):
                    # Delete the file
                    os.remove(file_path)
