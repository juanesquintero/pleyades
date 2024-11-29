import os
from flask import request, Blueprint, render_template, redirect, url_for
from dotenv import load_dotenv
from ast import literal_eval
from views.auth import only_admin
from services.API import get, put, delete

from utils.mixins import *

load_dotenv()

DatasetAdmin = Blueprint("DatasetAdmin", __name__)

endopoint = "datasets/"

upload_folder = os.getcwd() + "/uploads"


@DatasetAdmin.route("/")
@DatasetAdmin.route("/crudos")
@only_admin
def crudos():
    return get_list("crudos")


@DatasetAdmin.route("/enproceso")
@only_admin
def en_proceso():
    return get_list("en proceso")


@DatasetAdmin.route("/procesados")
@only_admin
def procesados():
    return get_list("procesados")


def get_list(status: str):
    status_p, body_p = get("programs")
    status_c, body_c = get("datasets/status/" + status)
    if status_c and status_p:
        return render_template(
            "admin/" + endopoint + status.replace(" ", "_") + ".html", datasets=body_c, programs=body_p
        )

    if not (status_c) and not (status_p):
        error = {**body_c, **body_p}
    elif not (status_c):
        error = body_c
    else:
        error = body_p
    return render_template(
        "admin/" + endopoint + status.replace(" ", "_") + ".html",
        datasets=[],
        error=error,
    )


@DatasetAdmin.route("/editar", methods=["POST"])
@only_admin
def post_edit():
    body = dict(request.values)
    conjunto = literal_eval(body["conjunto"])
    status_p, body_p = get("programs")
    if status_p:
        return render_template(
            "admin/" + endopoint + "editar.html", c=conjunto, programs=body_p
        )
    else:
        return render_template(
            "utils/message.html",
            mensaje="No se obtener los programs",
            submensaje=body_p,
        )


@DatasetAdmin.route("/actualizar", methods=["POST"])
@only_admin
def update():
    conjunto = dict(request.values)
    nombre = conjunto.pop("nombre")

    status, body = put("datasets/" + nombre, conjunto)
    if status:
        return redirect(url_for("DatasetAdmin.crudos"))

    return render_template(
        "utils/message.html",
        mensaje="No se pudo actualizar la conjunto",
        submensaje=body,
    )


@DatasetAdmin.route("/borrar", methods=["POST"])
@only_admin
def post_delete():
    body = dict(request.values)
    conjunto = literal_eval(body["conjunto"])
    status_p, body_p = get("programs")
    if status_p:
        return render_template(
            "admin/" + endopoint + "borrar.html", c=conjunto, programs=body_p
        )
    else:
        return render_template(
            "utils/message.html",
            mensaje="No se obtener los programs",
            submensaje=body_p,
        )


@DatasetAdmin.route("/remove", methods=["POST"])
@only_admin
def remove():
    conjunto = dict(request.values)
    nombre = conjunto.pop("nombre")
    status, body = delete("datasets/" + nombre)
    if status:
        # Eliminar archivos relacionados en el servidor
        exito, pagina_error = remove_file(
            upload_folder + "/crudos/" + "C " + nombre + ".xls"
        )
        if not (exito):
            return pagina_error
        if conjunto["status"] == "Procesados":
            exito, pagina_error = remove_file(
                upload_folder + "/procesados/" + "P " + nombre + ".xls"
            )
            if not (exito):
                return pagina_error

        return redirect(url_for("DatasetAdmin.crudos"))
    else:
        return render_template(
            "utils/message.html",
            mensaje="No se pudo Eliminar el conjunto",
            submensaje=body,
        )


@DatasetAdmin.route("/remove/todos", methods=["POST"])
@only_admin
def eliminar_todos():
    status = dict(request.values).pop("status")
    status, body = delete(f"datasets/todos/{status}")

    if status:
        # Eliminar archivos relacionados en el servidor
        remove_all_files(f"{upload_folder}/{status}")
        route = status.replace(" ", "_")
        return redirect(url_for(f"DatasetAdmin.{route}"))

    return render_template(
        "utils/message.html",
        mensaje="No se pudo Eliminar los datasets",
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
