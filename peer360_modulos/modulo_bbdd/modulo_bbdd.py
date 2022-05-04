import os
from flask import Blueprint, current_app, flash
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
# from sqlalchemy.orm import relationship

modulo_bbdd = Blueprint("modulo_bbdd", __name__,static_folder="static",template_folder="templates")

@modulo_bbdd.route('/modulo_bbdd/test')
def modulo_bbdd_test():
    return 'OK'

db = SQLAlchemy(current_app)


from modulo_funcionesAux.modulo_funcionesAux import df_global
# from modulo_assessment.modulo_assessment import send_email
from modulo_email.modulo_email import send_email


# LOGIN
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(200))
    confirmed = db.Column(db.Integer, default=0)
    userhash = db.Column(db.String(50))
    type_user = db.Column(db.Integer, default=1) # 0 es admin, 1 es usuario


    alumno = db.relationship('User_Group_Class', backref='user')


    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


from datetime import datetime
class Classes(db.Model):
    __tablename__='clases'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(20),unique=True)
    name = db.Column(db.String(50),unique=True)
    date = db.Column(db.DateTime)
    confirmed_groups = db.Column(db.Boolean)

    userref = db.relationship('User_Group_Class', backref='clases')
    peerref = db.relationship('PeerGrading', backref='clases')
    groupref = db.relationship('GroupGrading', backref='clases')


    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class PeerGrading(db.Model):
    __tablename__='peer_grading'
    id = db.Column(db.Integer, primary_key=True)
    #En una actividad...
    encuesta = db.Column(db.String(50), db.ForeignKey('clases.name'))
    #... un alumno...
    evaluador = db.Column(db.String(50), db.ForeignKey('user.email'))
    #... pone nota a otro alumno
    evaluado = db.Column(db.String(50), db.ForeignKey('user.email'))
    nota = db.Column(db.Float)

    Alumno_evaluador = db.relationship('User', foreign_keys = "PeerGrading.evaluador")
    Alumno_evaluado = db.relationship('User', foreign_keys = "PeerGrading.evaluado")
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class GroupGrading(db.Model):
    __tablename__='group_grading'
    id = db.Column(db.Integer, primary_key=True)
    #En una actividad...
    encuesta = db.Column(db.String(50), db.ForeignKey('clases.name'))
    #... un alumno...
    evaluador = db.Column(db.String(50), db.ForeignKey('user.email'))
    #... pone nota a un grupo
    grupo = db.Column(db.String(10))
    nota = db.Column(db.Float)

    Alumno_evaluador = db.relationship('User')

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class User_Group_Class(db.Model):
    __tablename__='grupos_clase'
    id = db.Column(db.Integer, primary_key=True)
    # ALVARO O JORGE: LA TUPLA DE ESTUDIANTE Y FILENAME DEBE SER ÚNICA
    # (En la inserción de datos os debeís de asegurar de que esta tupla es única (en el caso de que te vayan a meter algún dato donde esta condición falle, sobreescribir la tupla anterior))
    encuesta = db.Column(db.String(20), db.ForeignKey('clases.name'))
    email = db.Column(db.String(50), db.ForeignKey('user.email'))
    student_group = db.Column(db.String(80))

    #id_ref_1 = db.relationship('GroupGrading', backref='grupos_clase')
    #id_ref_2 = db.relationship('PeerGrading', backref='grupos_clase')
    # clases = db.relationship('Classes', backref='grupos_clase')

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


def save_groups(name,df_global):
    registeredUsers = User.query.filter(User.email).all()


    for index, row in df_global.iterrows():
        student_group = df_global["group"][index]
        student_mail = df_global["email"][index]
        student_name = df_global["name"][index]
        if (not student_mail in registeredUsers):
            try:
                nuevoUser = User(username=student_name, email=student_mail, password="1234", userhash="")
                db.session.add(nuevoUser)
                db.session.commit()
                send_email(student_mail,
                            'Your teacher has requested you an evaluation, you have been granted a user. Please change the default password and submit your grade', \
		                    'mail/email_requesting_assessment', url="http://davidgarcialleyda.pythonanywhere.com/login")
            except:
                db.session.rollback()
        try:
            user_group_class = User_Group_Class(encuesta=name, student_group=student_group,
                                                email=student_mail)
            db.session.add(user_group_class)
            db.session.commit()
        except:
            flash("Algo no ha ido bien ")
            db.session.rollback()


def save_file_in_db(filename, name, confirmed_groups="True"):
    clase = Classes.query.filter(Classes.filename == filename).first()

    if clase:
        clase.confirmed_groups = 1
        db.session.commit()
    else:
        new_class = Classes(filename=filename, name = name, date=datetime.now(), confirmed_groups=eval(confirmed_groups))
        db.session.add(new_class)
        db.session.commit()

def create_groups(df, encuesta):
    for index, row in df.iterrows():
        try:
            groupGrading = GroupGrading(encuesta = encuesta, evaluador = df["email"][index], grupo = df["groups"][index])
            db.session.add(groupGrading)
            db.session.commit()
        except:
            flash("El alumno " + df["email"][index]+ " no existe")
            print("El alumno " + df["email"][index]+ " no existe")

def create_peer(df, encuesta):
    for index, row in df.iterrows():
        try:
            peerGrading = PeerGrading(encuesta = encuesta, evaluador = df["email"][index], evaluado = df["email2"][index])
            db.session.add(peerGrading)
            db.session.commit()
        except:
            flash("El alumno " + df["email"][index]+ " no existe")
            print("El alumno " + df["email"][index]+ " no existe")