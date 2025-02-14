import os
from flask import request, Blueprint, render_template, redirect, url_for
from dotenv import load_dotenv
from ast import literal_eval
from web.views.auth import only_admin
from web.services.API import get, put, delete

from web.utils.mixins import *

load_dotenv()

DatasetAdmin = Blueprint("DatasetAdmin", __name__)

endopoint = "datasets/"

upload_folder = os.getcwd() + "/uploads"


@DatasetAdmin.route("/")
@DatasetAdmin.route("/raw")
@only_admin
def raw():
    return get_list("raw")


@DatasetAdmin.route("/enproceso")
@only_admin
def in_progress():
    return get_list("in progress")


@DatasetAdmin.route("/processed")
@only_admin
def processed():
    return get_list("processed")


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
    dataset = literal_eval(body["dataset"])
    status_p, body_p = get("programs")
    if status_p:
        return render_template(
            "admin/" + endopoint + "editar.html", c=dataset, programs=body_p
        )
    else:
        return render_template(
            "utils/message.html",
            message="No se get los programs",
            submensaje=body_p,
        )


@DatasetAdmin.route("/update", methods=["POST"])
@only_admin
def update():
    dataset = dict(request.values)
    name = dataset.pop("name")

    status, body = put("datasets/" + name, dataset)
    if status:
        return redirect(url_for("DatasetAdmin.raw"))

    return render_template(
        "utils/message.html",
        message="No se pudo update la dataset",
        submensaje=body,
    )


@DatasetAdmin.route("/delete", methods=["POST"])
@only_admin
def post_delete():
    body = dict(request.values)
    dataset = literal_eval(body["dataset"])
    status_p, body_p = get("programs")
    if status_p:
        return render_template(
            "admin/" + endopoint + "delete.html", c=dataset, programs=body_p
        )
    else:
        return render_template(
            "utils/message.html",
            message="No se get los programs",
            submensaje=body_p,
        )


@DatasetAdmin.route("/remove", methods=["POST"])
@only_admin
def remove():
    dataset = dict(request.values)
    name = dataset.pop("name")
    status, body = delete("datasets/" + name)
    if status:
        # Eliminar files relacionados en el servidor
        exito, pagina_error = remove_file(
            upload_folder + "/raw/" + "C " + name + ".xls"
        )
        if not (exito):
            return pagina_error
        if dataset["status"] == "Processed":
            exito, pagina_error = remove_file(
                upload_folder + "/processed/" + "P " + name + ".xls"
            )
            if not (exito):
                return pagina_error

        return redirect(url_for("DatasetAdmin.raw"))
    else:
        return render_template(
            "utils/message.html",
            message="No se pudo Eliminar el dataset",
            submensaje=body,
        )


@DatasetAdmin.route("/remove/todos", methods=["POST"])
@only_admin
def delete_todos():
    status = dict(request.values).pop("status")
    status, body = delete(f"datasets/todos/{status}")

    if status:
        # Eliminar files relacionados en el servidor
        remove_all_files(f"{upload_folder}/{status}")
        route = status.replace(" ", "_")
        return redirect(url_for(f"DatasetAdmin.{route}"))

    return render_template(
        "utils/message.html",
        message="No se pudo Eliminar los datasets",
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
