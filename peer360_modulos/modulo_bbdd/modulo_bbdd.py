import os
from flask import Blueprint, current_app
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

modulo_bbdd = Blueprint("modulo_bbdd", __name__,static_folder="static",template_folder="templates")

db = SQLAlchemy(current_app)


from modulo_funcionesAux.modulo_funcionesAux import df_global

class Student(db.Model):
    __tablename__='student'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50),unique=True)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

from datetime import datetime
class Classes(db.Model):
    __tablename__='clases'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(20),unique=True)
    date = db.Column(db.DateTime)
    confirmed_groups = db.Column(db.Boolean)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class PeerGrading(db.Model):
    __tablename__='peer_grading'
    id = db.Column(db.Integer, primary_key=True)
    id_user_group_class = db.Column(db.Integer, db.ForeignKey('grupos_clase.id'))
    grade = db.Column(db.Float)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class GroupGrading(db.Model):
    __tablename__='group_grading'
    id = db.Column(db.Integer, primary_key=True)

    id_user_group_class = db.Column(db.Integer, db.ForeignKey('grupos_clase.id'), unique=True)

    grade = db.Column(db.Float)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class User_Group_Class(db.Model):
    __tablename__='grupos_clase'
    id = db.Column(db.Integer, primary_key=True)
    #ALVARO O JORGE: LA TUPLA DE ESTUDIANTE Y FILENAME DEBE SER ÚNICA
    #(En la inserción de datos os debeís de asegurar de que esta tupla es única (en el caso de que te vayan a meter algún dato donde esta condición falle, sobreescribir la tupla anterior))
    filename = db.Column(db.String(20), db.ForeignKey('clases.filename'))
    student_mail = db.Column(db.String(50), db.ForeignKey('student.email'))
    student_group = db.Column(db.String(80))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


def save_groups(filename):
    for index, row in df_global.iterrows():
        student_group = df_global["group"][index]
        if("Username" in df_global.columns.values):
            student_mail = df_global["Username"][index]
        elif("email" in df_global.columns.values):
            student_mail = df_global["email"][index]
        else:
            student_mail = df_global["Nombre de usuario"][index]

        user_group_class = User_Group_Class(filename=filename, student_group=student_group, student_mail=student_mail)
        db.session.add(user_group_class)
        db.session.commit()

def save_file_in_db(filename, confirmed_groups="True"):
    new_class = Classes(filename=filename, date=datetime.now(), confirmed_groups=eval(confirmed_groups))
    db.session.add(new_class)
    db.session.commit()