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
    from modulo_bbdd.modulo_bbdd import *
    from modulo_uploadFile.modulo_uploadFile import *
    from modulo_assessment.modulo_assessment import *

app.register_blueprint(modulo_uploadFile)
app.register_blueprint(modulo_assessment)

# app.register_blueprint(modulo_funcionesAux)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

import json
with open('../configuration.json') as json_file:
    configuration = json.load(json_file)

# db = SQLAlchemy(app) # class db extends app

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}?auth_plugin=mysql_native_password".format(
  username=configuration["MYSQL_USERNAME"],
  password=configuration["MYSQL_PASSWORD"],
  hostname=configuration["MYSQL_HOSTNAME"],
  databasename=configuration["MYSQL_DATABASENAME"]
  )
app.config['SECRET_KEY'] = '37utopisdr jt ñçã3q0r9irjqwasdaADFSADF3q0r9irjqw'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = configuration['gmail_username']
app.config['MAIL_PASSWORD'] = configuration['gmail_password']
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[360 peer grading] '
app.config['FLASKY_MAIL_SENDER'] = 'Prof. Manoel Gadi'
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

    return render_template('showFiles.html',module="home", dataframes=dataframes, filtroActivo=filtro)

@app.route('/main_page/test')
def app_test():
    return 'OK'

# #import base64
# @app.route('/degree360')
# def degree360():
#     filename = request.cookies.get('filename')
#     #token=generate_password_hash(filename,method="sha256")
#     token= filename
#     # enc = base64.b64decode(enc)
#     url = "{}/assess?type=degree360&token={}".format(configuration["base_url"], token)
#     df = pd.read_excel(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#     #form.course_id.default = request.cookies.get('course_id')
#     #return '<h1>360degree - last filename uploaded: ' + name + '</h1>'
#     return render_template('degree360.html',module="degree360",df_html=df.fillna('').to_html(),url=url)

# @app.route('/peergrading')
# def peergrading():
#     filename = request.cookies.get('filename')
#     token= filename
#     url = "{}/assess?type=peergrading&token={}".format(configuration["base_url"], token)
#     df = pd.read_excel(os.path.join(app.config['UPLOAD_FOLDER'], filename))
# 	#form.course_id.default = request.cookies.get('course_id')
#     return render_template('peergrading.html',module="peergrading",df_html=df.fillna('').to_html(),url=url)


# @app.route('/request_assessment/<type>')    #int has been used as a filter that only integer will be passed in the url otherwise it will give a 404 error
# def request_assessment(type):
# 	filename = request.cookies.get('filename')
# 	df = pd.read_excel(os.path.join(app.config['UPLOAD_FOLDER'], filename))
# 	for i in range(len(df)):
# 		token=generate_password_hash(str(df['name'].iloc(i))+filename,method="sha256")
# 		url = "http://localhost:5000/assess?type={}&email={}&filename={}&token={}".format(type, \
# 		df['email'].iloc[i],filename,token)
# 		send_email(str(df['email'].iloc[i]),'Please assess your colleagues.', \
# 		'mail/email_requesting_assessment',url=url)
# 	return "sucessfully sent request to all users!"



# @app.route('/assess', methods=['GET','POST'])
# def assess():
#     if request.method == 'GET':
#         filename = request.args.get("token")
#         if filename:
#             #try:#2zBdEa9Ilh.xlsx
#             df = pd.read_excel(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             try:
#                 name = str(df[df["email"]==request.args.get("email")]["name"].iloc[0])
#                 str_encoded = request.args.get("email")[1:2] + name[2:4] + request.args.get('token')[8:10]
#                 if str_encoded == request.cookies.get('pin'):
#                     # 1) Leer los datos que  request.form.get("email") tiene que editar llevando en consideración ekl tipo:  request.args.get('type') .
#                     if request.args.get('type') == "peergrading": #Evaluar a los demás grupos
#                         df = pd.read_excel(os.path.join(app.config['UPLOAD_FOLDER'], filename),sheet_name="group")
#                         groups = df[df["email"]==request.args.get("email")]["groups"].unique()
#                         return render_template("grade_other_groups.html",groups = groups)

#                     elif request.args.get('type') == "degree360": #Evaluar a los demás de tu grupo

#                         df = pd.read_excel(os.path.join(app.config['UPLOAD_FOLDER'], filename),sheet_name="360")
#                         emails = df[df["email"]==request.args.get("email")]["email2"]
#                         return render_template("grade_360.html",emails = emails)
#                     else:
#                         return "wrong type"

#                     return request.cookies.get('pin')
#             except:
#                 return render_template("confirm_email.html",type=request.args.get('type'),token=request.args.get('token'))
#     else:
#         filename = request.form.get("token")
#         if filename:
#             #try:#2zBdEa9Ilh.xlsx
#             df = pd.read_excel(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             if (len(df[df["email"]==request.form.get("email")])>0): #Existe el correo
#                 name = str(df[df["email"]==request.form.get("email")]["name"].iloc[0])
#                 str_encoded = request.form.get("email")[1:2] + name[2:4] + request.form.get('token')[8:10]
#                 #return str_encoded
#                 #str_encoded =  #cryptocode.encrypt(str(df[df["email"]==request.form.get("email")]["name"].iloc[0])[0:4],"wow")
# #                    return str_encoded[0:4]
#                 send_email(request.form.get("email"),'Please assess your colleagues.', 'mail/email_requesting_assessment',url=str_encoded)

#                 response = make_response(redirect(url_for('assessing',
#                                         type=request.form.get("type"),
#                                         token=request.form.get("token"),
#                                         email=request.form.get("email"))))
#                 return response
#                 #return df[df["email"]==request.form.get("email")].to_html()
#             else:
#                 return "Wrong email!"
#             #except:
#             #    #flash("Wrong url!")
#             #    return "Wrong url!"
#         else:
#             return "Wrong url!"

# @app.route('/update_other_groups', methods=['GET','POST'])
# def update_other_groups():
#     return "update_other_groups"

# @app.route('/update_peer360', methods=['GET','POST'])
# def update_peer360():
#     return "update_peer360"

# @app.route('/assessing', methods=['GET','POST'])
# def assessing():
#     if request.method == 'GET':
#         return render_template("confirm_pin.html",type=request.args.get('type'),token=request.args.get('token'), email=request.args.get('email'))
#     else:
# #        return request.form.get("pin")
#         filename = request.form.get("token")
#         if filename:
#             try:#
#                 df = pd.read_excel(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#                 if (len(df[df["email"]==request.form.get("email")])>0): #Existe el correo
#                     name = str(df[df["email"]==request.form.get("email")]["name"].iloc[0])
#                     str_encoded = request.form.get("email")[1:2] + name[2:4] + request.form.get('token')[8:10]
#                     if str_encoded == request.form.get("pin"):
#                         #return "ACCESO LIBERADO"
#                         response = make_response(redirect(url_for('assess',
#                                         type=request.form.get("type"),
#                                         token=request.form.get("token"),
#                                         email=request.form.get("email"))))
#                         response.set_cookie('pin', request.form.get("pin"))
#                         return response
#                     else:
#                         return "ACCESS DENIED"
#             except:
#                 #flash("Wrong url!")
#                 return "Wrong url!"


# @app.route('/setcookie')
# def setcookie():
#     mycookie = str(request.args.get('name'))
#     response = make_response(redirect(url_for('index',
#                             filename='yyy')))
#     response.set_cookie('miprimeracookie', mycookie)
#     return response

# @app.route('/getcookie')
# def getcookie():
#     return request.cookies.get('miprimeracookie')