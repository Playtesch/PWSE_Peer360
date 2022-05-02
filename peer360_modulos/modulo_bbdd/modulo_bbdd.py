import os
from flask import Blueprint, current_app
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

modulo_bbdd = Blueprint("modulo_bbdd", __name__, static_folder="static", template_folder="templates")

@modulo_bbdd.route('/test')
def modulo_bbdd_test():
    return 'OK'

db = SQLAlchemy(current_app)

from modulo_funcionesAux.modulo_funcionesAux import df_global
# from modulo_assessment.modulo_assessment import send_email
from modulo_email.modulo_email import send_email


# LOGIN
class User(db.Model, UserMixin):
    __tablename__ = 'userPeer'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(200))
    confirmed = db.Column(db.Integer, default=0)
    userhash = db.Column(db.String(50))
    type_user = db.Column(db.Integer, default=1)  # 0 es admin, 1 es usuario

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# class Student(db.Model):
#     __tablename__='student'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50))
#     email = db.Column(db.String(50),unique=True)

#     def as_dict(self):
#         return {c.name: getattr(self, c.name) for c in self.__table__.columns}

from datetime import datetime


class Classes(db.Model):
    __tablename__ = 'clases'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(20), unique=True)
    date = db.Column(db.DateTime)
    confirmed_groups = db.Column(db.Boolean)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class PeerGrading(db.Model):
    __tablename__ = 'peer_grading'
    id = db.Column(db.Integer, primary_key=True)
    id_user_group_class = db.Column(db.Integer, db.ForeignKey('grupos_clase.id'))
    grade = db.Column(db.Float)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class GroupGrading(db.Model):
    __tablename__ = 'group_grading'
    id = db.Column(db.Integer, primary_key=True)

    id_user_group_class = db.Column(db.Integer, db.ForeignKey('grupos_clase.id'), unique=True)

    grade = db.Column(db.Float)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class User_Group_Class(db.Model):
    __tablename__ = 'grupos_clase'
    id = db.Column(db.Integer, primary_key=True)
    # ALVARO O JORGE: LA TUPLA DE ESTUDIANTE Y FILENAME DEBE SER ÚNICA
    # (En la inserción de datos os debeís de asegurar de que esta tupla es única (en el caso de que te vayan a meter algún dato donde esta condición falle, sobreescribir la tupla anterior))
    filename = db.Column(db.String(20), db.ForeignKey('clases.filename'))
    student_mail = db.Column(db.String(50), db.ForeignKey('userPeer.email'))
    student_group = db.Column(db.String(80))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


def save_groups(filename, df_global):
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
            user_group_class = User_Group_Class(filename=filename, student_group=student_group,
                                                student_mail=student_mail)
            db.session.add(user_group_class)
            db.session.commit()
        except:
            db.session.rollback()

        # if("Username" in df_global.columns.values):
        #     student_mail = df_global["Username"][index]
        # elif("email" in df_global.columns.values):
        #     student_mail = df_global["email"][index]
        # else:
        #     student_mail = df_global["Nombre de usuario"][index]

    # try:


# except Exception:
# print(Exception.__traceback__)
# print("No se pudo meter en bbdd los grupos")
# db.session.rollback()

def save_file_in_db(filename, confirmed_groups="True"):
    clase = Classes.query.filter(Classes.filename == filename).first()

    if clase:
        clase.confirmed_groups = 1
        db.session.commit()
    else:
        new_class = Classes(filename=filename, date=datetime.now(), confirmed_groups=eval(confirmed_groups))
        db.session.add(new_class)
        db.session.commit()
