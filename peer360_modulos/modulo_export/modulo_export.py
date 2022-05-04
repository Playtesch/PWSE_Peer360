import os
from flask import Blueprint, request, send_file, render_template, make_response, url_for, redirect, current_app
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from modulo_funcionesAux.modulo_funcionesAux import *
modulo_export = Blueprint("modulo_export", __name__,static_folder="static",template_folder="templates")

@modulo_export.route("/download_file/<string:filename>/<string:name>", methods=['GET', 'POST'])
def download_file(filename, name):

    extension = get_extension(filename)

    return send_file(os.path.join(current_app.config['UPLOAD_FOLDER'],filename), attachment_filename=name+"."+extension)
    # return make_response(redirect(url_for('/')))
@modulo_export.route("/download_notas/<string:filename>", methods=['GET', 'POST'])
def download_notas(filename):
    return send_file(os.path.join(current_app.config['DATA'],filename), attachment_filename=filename)
    # return make_response(redirect(url_for('/')))

@modulo_export.route('/modulo_export/test')
def modulo_export_test():
    return 'OK'