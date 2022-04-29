import os
import random
from flask import Flask, flash, request, redirect, url_for, render_template, make_response
# from flask_login import LoginManager, login_required, login_user, current_user, logout_user, UserMixin
# from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask_mail import Mail, Message


app = Flask(__name__)

with app.app_context():
    from modulo_funcionesAux.modulo_funcionesAux import *

    app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[360 peer grading] '
    app.config['FLASKY_MAIL_SENDER'] = 'Prof. Manoel Gadi'
    app.config['MAIL_USERNAME'] = get_configuration()['gmail_username']
    app.config['MAIL_PASSWORD'] = get_configuration()['gmail_password']

    from modulo_bbdd.modulo_bbdd import *
    from modulo_uploadFile.modulo_uploadFile import *
    from modulo_assessment.modulo_assessment import *
    from modulo_forms.modulo_forms import *
    from modulo_export.modulo_export import modulo_export

app.register_blueprint(modulo_uploadFile)
app.register_blueprint(modulo_assessment)
app.register_blueprint(modulo_export)

# app.register_blueprint(modulo_funcionesAux)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# import json
# with open('../configuration.json') as json_file:
#     configuration = json.load(json_file)

# db = SQLAlchemy(app) # class db extends app

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}?auth_plugin=mysql_native_password".format(
  username=get_configuration()["MYSQL_USERNAME"],
  password=get_configuration()["MYSQL_PASSWORD"],
  hostname=get_configuration()["MYSQL_HOSTNAME"],
  databasename=get_configuration()["MYSQL_DATABASENAME"]
  )
app.config['SECRET_KEY'] = '37utopisdr jt ñçã3q0r9irjqwasdaADFSADF3q0r9irjqw'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# mail = Mail(app)


# def send_email(to, subject, template, url, **kwargs):
#     msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject, sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
#     msg.body = render_template(template + '.txt', **kwargs, url=url)
#     msg.html = render_template(template + '.html', **kwargs, url=url)
#     # flash("send_email: {}".format(url))
#     mail.send(msg)

#import pandas as pd
@app.route('/')
def index():
    if request.cookies.get('filename'):
        return render_template('index.html',module="home",cookie=True)
    else:
        return render_template('index.html',module="home")



df_global = None


@app.route('/show_files', methods=['GET', 'POST'])
def show_files():

    print("He entrado a show_files")

    excelFiles = None

    if (request.method == 'POST'):
        filtro = request.form.get('filtro')

        if (filtro == 'Más reciente'):
            excelFiles = [r.filename for r in Classes.query.order_by(Classes.date.desc()).all()]
        elif (filtro == 'Más antiguo'):
            excelFiles = [r.filename for r in Classes.query.order_by(Classes.date).all()]
        elif (filtro == 'Orden alfabético'):
            excelFiles = [r.filename for r in Classes.query.order_by(Classes.filename).all()]
        else:
            excelFiles = [r.filename for r in Classes.query.order_by(Classes.filename.desc()).all()]
    else:
        filtro = 'Más reciente'
        excelFiles = [r.filename for r in Classes.query.order_by(Classes.date.desc()).all()]

    print("Estoy mostrando los excels")
    print(type(excelFiles))
    print("Hasta aqui el tipo de excelFiles\nAhora los contenidos de excelFiles")
    print(excelFiles)
    dataframes = [pd.read_excel(os.path.join(app.config['UPLOAD_FOLDER'],i)).to_html() for i in excelFiles]

    lista = list(zip(excelFiles, dataframes))

    return render_template('showFiles.html',module="home", dataframes=dataframes, filtroActivo=filtro, lista=lista)

