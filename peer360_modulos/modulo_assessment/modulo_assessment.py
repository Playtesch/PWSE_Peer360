import os
from flask import Blueprint, render_template, current_app, url_for, request, redirect, make_response, flash
from flask_login import current_user
import random
# from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash
import pandas as pd

modulo_assessment = Blueprint("modulo_assessment", __name__,static_folder="static",template_folder="templates")

from modulo_funcionesAux.modulo_funcionesAux import get_configuration, getConfirmed
from modulo_bbdd.modulo_bbdd import *
from modulo_email.modulo_email import send_email
from modulo_forms.modulo_forms import GradingForm
df_global = None

# mail = Mail(current_app)

# def send_email(to, subject, template, url, **kwargs):
#     print("Url: {} ".format(url))
#     msg = Message(current_app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject, sender=current_app.config['FLASKY_MAIL_SENDER'], recipients=[to])
#     msg.body = render_template(template + '.txt', **kwargs, url=url)
#     msg.html = render_template(template + '.html', **kwargs, url=url)
#     # flash("send_email: {}".format(url))
#     print("El email va a ser:{}".format(msg))
#     print("El body va a ser:{}".format(msg.body))
#     print("El html va a ser:{}".format(msg.html))
#     mail.send(msg)

@modulo_assessment.route('/modulo_assessment/test')
def modulo_assessment_test():
    return 'OK'

#import base64
@modulo_assessment.route('/degree360')
def degree360():

    url = "{}/assess2?type=degree360".format(get_configuration()["base_url"])
    return redirect(url)

    # filename = request.cookies.get('filename')
    # confirmed = getConfirmed()

    # if confirmed:
    #     group_grading=""
    #     try:
    #         group_grading = request.cookies.get('group_grading')
    #     except:
    #         group_grading = "True"

    #     #token=generate_password_hash(filename,method="sha256")
    #     token= filename
    #     # enc = base64.b64decode(enc)
    #     try:
    #         df = pd.read_excel(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    #         #form.course_id.default = request.cookies.get('course_id')
    #         #return '<h1>360degree - last filename uploaded: ' + name + '</h1>'
    #         return render_template('degree360.html',module="degree360",df_html=df.fillna('').to_html(),url=url, group_grading=group_grading)
    #     except:
    #         flash("Todavía tienes que subir un fichero")
    #         response = make_response(redirect(url_for('modulo_uploadFile.upload_file')))
    #         return response
    # else:
    #     flash("Todavía los grupos no se han confirmado")
    #     response = make_response(redirect(url_for('index')))
    #     return response




# @modulo_assessment.route('/peergrading')
# def peergrading():
#     filename = request.cookies.get('filename')

#     confirmed = getConfirmed()

#     df = pd.read_excel(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))


#     group_grading = False
#     if confirmed:
#         if pd.isna(df["group"].iloc[0]):
#             group_grading = False
#         else:
#             group_grading = True

#     if group_grading:
#         token= filename
#         url = "{}/assess?type=peergrading&token={}".format(get_configuration()["base_url"], token)
#         try:
#             df = pd.read_excel(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
#     	#form.course_id.default = request.cookies.get('course_id')
#             return render_template('peergrading.html',module="peergrading",df_html=df.fillna('').to_html(),url=url)
#         except:
#             flash("Todavía tienes que subir un fichero")
#             response = make_response(redirect(url_for('modulo_uploadFile.upload_file')))
#             return response
#     else:
#         flash("No hay grupos para esta clase")
#         response = make_response(redirect(url_for('index')))
#         return response

@modulo_assessment.route('/peergrading')
def peergrading():

    url = "{}/assess2?type=peergrading".format(get_configuration()["base_url"])

    	#form.course_id.default = request.cookies.get('course_id')
    return redirect(url)
    # return render_template('peergrading.html',module="peergrading",url=url)




@modulo_assessment.route('/request_assessment/<tipo>/<encuesta>')
def request_assessment(tipo, encuesta):

# 	if 'Nombre de usuario' in df.columns or 'Username' in df.columns:
# 	    df = df.rename(columns={df.columns[2]:'email', df.columns[1]:'name'})
    users = User.query.filter(User.encuesta == encuesta)
    for user in users:
	    url = "{}/assess2?type={}".format(get_configuration()["base_url"], tipo)
	    send_email(user.email,'Please assess your colleagues.', \
	    'mail/email_requesting_assessment',url=url)
    flash("sucessfully sent request to all users!")

    return make_response(redirect(url_for("modulo_assessment."+tipo)))



# @modulo_assessment.route('/assess', methods=['GET','POST'])
# def assess():

#     print("He hecho una peticion a assess de tipo: {}".format(request.method))

#     if request.method == 'GET':
#         filename = request.args.get("token")

#         group_grading=""
#         try:
#             group_grading = request.cookies.get('group_grading')
#         except:
#             group_grading = "True"
#         if filename:
#             #try:#2zBdEa9Ilh.xlsx

#             df = pd.read_excel(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

#             try:
#                 # if 'Nombre de usuario' or 'Username' in df.columns:
#                 #     df = df.rename(columns={df.columns[2]: 'email', df.columns[1]:"name"})

#                 name = str(df[df["email"]==request.args.get("email")]["name"].iloc[0])

#                 print("El name recogido es:" + name)

#                 str_encoded = request.args.get("email")[1:2] + name[2:4] + request.args.get('token')[8:10]
#                 if str_encoded == request.cookies.get('pin'):

#                     print("Linea 104 modulo_assessment, has acertado el pin")

#                     print("El tipo que tiene que acceder es: " + request.args.get('type'))
#                     # 1) Leer los datos que  request.form.get("email") tiene que editar llevando en consideración ekl tipo:  request.args.get('type') .
#                     if request.args.get('type') == "peergrading": #Evaluar a los demás grupos

#                         df = pd.read_excel(os.path.join(current_app.config['UPLOAD_FOLDER'], filename),sheet_name="group")

#                         print("El df leido del peergrading de la hoja group es: {}".format(df))
#                         print("Las columnas son {}".format(df.columns))


#                         groups = df[df["email"]==request.args.get("email")]["groups"].unique()
#                         return render_template("grade_other_groups.html",groups = groups)

#                     elif request.args.get('type') == "degree360": #Evaluar a los demás de tu grupo
#                         print("He entrado al degree360")

#                         df = pd.read_excel(os.path.join(current_app.config['UPLOAD_FOLDER'], filename),sheet_name="360")

#                         print("El dataframe leido es {}".format(df))
#                         print("El dataframe leido tiene las columnas: {}".format(df.columns))

#                         print("El dataframe donde coincide el email es:")
#                         print(df[df["email"]==request.args.get("email")])

#                         emails = df[df["email"]==request.args.get("email")]["email2"]

#                         print("Los emails que tengo que evaluar son:")
#                         print(*emails, sep='\n')

#                         return render_template("grade_360.html",emails = emails)
#                     else:
#                         return "wrong type"

#                     return request.cookies.get('pin')
#             except:

#                 print("No has acertado el pin o request.cookies.get('pin') da error")

#                 return render_template("confirm_email.html",type=request.args.get('type'),token=request.args.get('token'), group_grading=group_grading)
#     else:
#         filename = request.form.get("token")

#         if filename:
#             #try:#2zBdEa9Ilh.xlsx
#             df = pd.read_excel(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))


#             print("Email pasado a traves del formulario es:" + request.form.get("email"))
#             print("Print el dataframe con los emails es: {}".format(df["email"]))

#             print("El email coincidente es: {}".format(df[df["email"]==request.form.get("email")]))

#             print("La longitud del email coincidente es:" + str(len(df[df["email"]==request.form.get("email")])))

#             if (len(df[df["email"]==request.form.get("email")])>0): #Existe el correo
#                 name = str(df[df["email"]==request.form.get("email")]["name"].iloc[0])

#                 print("El nombre recogido es: " + name)

#                 str_encoded = request.form.get("email")[1:2] + name[2:4] + request.form.get('token')[8:10]
#                 #return str_encoded
#                 #str_encoded =  #cryptocode.encrypt(str(df[df["email"]==request.form.get("email")]["name"].iloc[0])[0:4],"wow")
# #                    return str_encoded[0:4]
#                 print("Email recibido: "+request.form.get("email"))
#                 send_email(request.form.get("email"),'Please assess your colleagues.', 'mail/email_requesting_assessment',url=str_encoded)

#                 response = make_response(redirect(url_for('modulo_assessment.assessing',
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


@modulo_assessment.route('/assess2', methods=['GET','POST'])
def assess2():
    if request.method == 'GET':
        pin = ''.join(random.choice('AILNOQVBCDEFGHJKMPRSTUXZabcdefghijklmnopqrstuvxz1234567890') for i in range(4))

        current_user.userhash = pin

        try:
            db.session.commit()
        except:
            db.session.rollback()

        return render_template("confirm_email.html",type=request.args.get('type'))
    else:

        pin = current_user.userhash

        print("El pin leido de la base de datos es: {}".format(pin))

        # pin = request.form.get('pin')
        email = request.form.get('email')
        tipo = request.form.get('type')

        send_email(request.form.get("email"),'Please assess your colleagues.', 'mail/email_requesting_assessment',url=pin)

        response = make_response(redirect(url_for('modulo_assessment.assessing2',
                                tipo=tipo,
                                email=email)))
        return response



@modulo_assessment.route('/assessing2', methods=['GET','POST'])
def assessing2():

    print("Se ha hecho una peticion a /assessing de tipo: " + request.method)

    if request.method == 'GET':

        return render_template("confirm_pin.html",tipo=request.args.get('tipo'),pin=request.args.get('pin'), email=request.args.get('email'))
    else:
        if current_user.userhash == request.form.get("pin"):

            current_user.userhash = ""
            try:
                db.session.commit()
            except:
                db.session.rollback()

            if request.form.get("tipo") == "peergrading":
                response = make_response(redirect(url_for('modulo_assessment.grade_other_groups')))
            elif request.form.get("tipo") == "degree360":
                response = make_response(redirect(url_for('modulo_assessment.grade_other_students')))
            return response
        else:
            return "ACCESS DENIED"






@modulo_assessment.route('/update_other_groups', methods=['GET','POST'])
def update_other_groups():
    return "update_other_groups"

@modulo_assessment.route('/update_peer360', methods=['GET','POST'])
def update_peer360():
    return "update_peer360"

# @modulo_assessment.route('/assessing', methods=['GET','POST'])
# def assessing():

#     print("Se ha hecho una peticion a /assessing de tipo: " + request.method)

#     if request.method == 'GET':

#         group_grading = ""

#         try:
#             group_grading = request.cookies.get('group_grading')
#         except:
#             group_grading = "True"
#         return render_template("confirm_pin.html",type=request.args.get('type'),token=request.args.get('token'), email=request.args.get('email'), group_grading = group_grading)
#     else:
# #        return request.form.get("pin")
#         filename = request.form.get("token")
#         if filename:
#             try:#
#                 df = pd.read_excel(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
#                 # if 'Nombre de usuario' or 'Username' in df.columns:
#                 #     df = df.rename(columns={df.columns[2]: 'email'})
#                 if (len(df[df["email"]==request.form.get("email")])>0): #Existe el correo
#                     name = str(df[df["email"]==request.form.get("email")]["name"].iloc[0])
#                     str_encoded = request.form.get("email")[1:2] + name[2:4] + request.form.get('token')[8:10]
#                     if str_encoded == request.form.get("pin"):
#                         print("ACCESO LIBERADO")
#                         print(request.form.get("type"))

#                         ##################### AQUI CAMBIAR EL REDIRECT SEGUN EL TYPE PARA GRADE_OTHER_GROUPS
#                         if request.form.get("type") == "peergrading":
#                             response = make_response(redirect(url_for('modulo_assessment.grade_other_groups',
#                                             token=request.form.get("token"))))
#                         elif request.form.get("type") == "degree360":
#                             print("HEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEY")
#                             print("Voy a evaluar a otro alumnos")
#                             response = make_response(redirect(url_for('modulo_assessment.grade_other_students',
#                                             token=request.form.get("token"))))
#                         return response
#                     else:
#                         return "ACCESS DENIED"
#             except Exception as e:
#                 #flash("Wrong url!")
#                 print(e)
#                 return "Wrong url!"

@modulo_assessment.route('/grade_other_groups', methods=['GET', 'POST'])
def grade_other_groups():
    forms = []
    if (request.method == 'POST'):
        form = GradingForm()
        filename = form.encuesta.data
        evaluado = GroupGrading.query.filter(GroupGrading.encuesta == filename, GroupGrading.evaluador == current_user.email, GroupGrading.grupo == form.evaluado.data).first()
        evaluado.nota = form.grade.data
        db.session.commit()

    evaluar = GroupGrading.query.filter(GroupGrading.evaluador == current_user.email, GroupGrading.nota == None).all()
    for item in evaluar:
        form = GradingForm()
        form.encuesta.data = item.encuesta
        form.evaluado.data = item.grupo
        forms.append(form)


    return render_template('grade_other_groups.html', module = "home",forms = forms)

@modulo_assessment.route('/grade_other_students', methods=['GET', 'POST'])
def grade_other_students():
    forms = []
    if (request.method == 'POST'):
        form = GradingForm()
        filename = form.encuesta.data
        evaluado = PeerGrading.query.filter(PeerGrading.encuesta == filename, PeerGrading.evaluador == current_user.email, PeerGrading.evaluado == form.evaluado.data).first()
        evaluado.nota = form.grade.data
        db.session.commit()
    else:
        filename = request.args.get("token")

    evaluar = PeerGrading.query.filter(PeerGrading.evaluador == current_user.email, PeerGrading.nota == None).all()

    for item in evaluar:
        form = GradingForm()
        form.encuesta.data = item.encuesta
        form.evaluado.data = item.evaluado
        forms.append(form)


    return render_template('grade_other_students.html', module = "home",forms = forms)