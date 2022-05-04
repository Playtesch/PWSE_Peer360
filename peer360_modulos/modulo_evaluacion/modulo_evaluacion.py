from flask import Blueprint, render_template, current_app, flash, request, redirect, url_for, make_response

modulo_evaluacion = Blueprint("modulo_evaluacion", __name__,static_folder="static",template_folder="templates")
import functools
from modulo_bbdd.modulo_bbdd import GroupGrading, PeerGrading, User_Group_Class
from modulo_funcionesAux.modulo_funcionesAux import *
from modulo_email.modulo_email import send_email




@modulo_evaluacion.route('/detalle_encuesta/<encuesta>', methods = ["GET","POST"])
def detalle_encuesta(encuesta):
    urlpeer = "{}/assess2?type=peergrading".format(get_configuration()["base_url"], request.form.get("tipo"))
    url360 = "{}/assess2?type=degree360".format(get_configuration()["base_url"], request.form.get("tipo"))
    if request.method == "POST":
        users = User_Group_Class.query.filter(User_Group_Class.encuesta == encuesta).all()
        for user in users:
    	    send_email(user.email,'Please assess your colleagues.', \
    	    'mail/email_requesting_assessment',url=urlpeer)
    	    send_email(user.email,'Please assess your colleagues.', \
    	    'mail/email_requesting_assessment',url=url360)
    	    print(user.email)
        flash("sucessfully sent request to all users!")

    total = 0
    contestado = 0
    evaluacion = PeerGrading.query.filter(PeerGrading.encuesta == encuesta)
    notas = []
    for item in evaluacion:
        total +=1
        if item.nota:
            contestado +=1
            notas.append(item.nota)
    try:
        alumnos_respon = str(contestado/total*100)+"%"
    except:
        alumnos_respon = "No hay evaluacion"
    try:
        media_alumnos = "{:.2f}".format(functools.reduce(lambda x, y: x+y, notas)/contestado)
        normal_alumnos = "{:.2f}".format(functools.reduce(lambda x, y: x+y, map(lambda x: x*10/max(notas), notas))/contestado)
    except:
        media_alumnos = "No hay respuestas"
        normal_alumnos = "No hay respuestas"

    total = 0
    contestado = 0
    evaluacion = GroupGrading.query.filter(GroupGrading.encuesta == encuesta).all()
    notas = []
    for item in evaluacion:
        total +=1
        if item.nota:
            contestado +=1
            notas.append(item.nota)
    try:
        grupos_respon = str(contestado/total*100) + "%"
    except:
        grupos_respon = "No hay evaluacion"
    try:
        media_grupos = "{:.2f}".format(functools.reduce(lambda x, y: x+y, notas)/contestado)
        normal_grupos = "{:.2f}".format(functools.reduce(lambda x, y: x+y, map(lambda x: x*10/max(notas), notas))/contestado)
    except:
        media_grupos = "No hay respuestas"
        normal_grupos = "No hay respuestas"
    return render_template('detalle_encuesta.html', encuesta=encuesta,
                        alumnos=alumnos_respon,
                        grupos=grupos_respon,
                        media_alumnos = media_alumnos,
                        normal_alumnos = normal_alumnos,
                        media_grupos = media_grupos,
                        normal_grupos = normal_grupos,
                        urlpeer = urlpeer,
                        url360= url360)

@modulo_evaluacion.route('/notas_encuesta/<encuesta>/<tipo>', methods = ["GET"])
def notas_encuesta(encuesta, tipo):
    notas = []
    notas_dict = {}
    notas_final = []
    if tipo == "peergrading":
        evaluado = "Grupo"
        users = GroupGrading.query.filter(GroupGrading.encuesta == encuesta).all()
        for user in users:
            notas.append( (user.evaluador, user.grupo, user.nota) )
            try:
                if user.nota:
                    notas_dict[user.grupo].append(user.nota)
            except:
                if user.nota:
                    notas_dict[user.grupo]= [user.nota]

        for key in notas_dict.keys():
            notas_final.append( (key, "{:.2f}".format(functools.reduce(lambda x, y: x+y, notas_dict[key])/len(notas_dict[key])),
                        "{:.2f}".format(functools.reduce(lambda x, y: x+y, map(lambda x: x*10/max(notas_dict[key]), notas_dict[key]))/len(notas_dict[key]))))

    elif tipo == "degree360":
        evaluado = "Alumno"
        users = PeerGrading.query.filter(PeerGrading.encuesta == encuesta).all()
        for user in users:
            notas.append( (user.evaluador, user.evaluado, user.nota) )
            try:
                if user.nota:
                    notas_dict[user.evaluado].append(user.nota)
            except:
                if user.nota:
                    notas_dict[user.evaluado]= [user.nota]
        for key in notas_dict.keys():
            notas_final.append( (key, "{:.2f}".format(functools.reduce(lambda x, y: x+y, notas_dict[key])/len(notas_dict[key])),
                        "{:.2f}".format(functools.reduce(lambda x, y: x+y, map(lambda x: x*10/max(notas_dict[key]), notas_dict[key]))/len(notas_dict[key]))))
    #list_students.sort(key = lambda x: x[1])   #index 1 means second element
    notas.sort(key= lambda x: x[0])
    notas_final.sort(key= lambda x: x[0])
    writeExcel(encuesta+"_evaluacion", notas,["Evaluador",	"Grupo",	"Nota"] )
    writeExcel(encuesta+"_promedios", notas_final, ["Grupo",	"Nota media",	"Nota media normalizada"])
    return render_template('notas_encuesta.html', encuesta=encuesta, tipo = evaluado, evaluacion = notas, notas = notas_final)



# 1 grupo: B, nota: [asjd,asda,asdhcas,asdiajs,asdica]




    #name, [(evaluado, media, normal)]

# @modulo_assessment.route('/request_assessment/<tipo>/<encuesta>')
# def request_assessment(tipo, encuesta):

# # 	if 'Nombre de usuario' in df.columns or 'Username' in df.columns:
# # 	    df = df.rename(columns={df.columns[2]:'email', df.columns[1]:'name'})
#     users = User.query.filter(User.encuesta == encuesta)
#     for user in users:
# 	    url = "{}/assess2?type={}".format(get_configuration()["base_url"], tipo)
# 	    send_email(user.email,'Please assess your colleagues.', \
# 	    'mail/email_requesting_assessment',url=url)
#     flash("sucessfully sent request to all users!")

    # return make_response(redirect(url_for("modulo_assessment."+tipo)))