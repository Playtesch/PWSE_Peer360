from flask import Blueprint, current_app
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

modulo_bbdd = Blueprint("modulo_bbdd", __name__,static_folder="static",template_folder="templates")

@modulo_bbdd.route('/modulo_bbdd/test')
def modulo_bbdd_test():
    return 'OK'

db = SQLAlchemy(current_app)

from modulo_funcionesAux.modulo_funcionesAux import get_df_from_file

#Una sola clase para estudiantes y usuarios
class Estudiante(db.Model):
    __tablename__='estudiantes'
    email = db.Column(db.String(50),primary_key=True)
    nombre = db.Column(db.String(20))
    apellido = db.Column(db.String(20))
    nombre_usuario = db.Column(db.String(20), unique=True)
    #Datos para login
    password = db.Column(db.String(200))
    confirmed = db.Column(db.Int)
    userhash = db.Column(db.String(50))
    tipo = db.Column(db.Int) #Profesor o estudiante

    #ultimo_acceso = db.Column(db.DateTime) Actualizar este campo al hacer login

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# Actividad que descarga el profe de bb, solo el nombre y datos extra
class Encuesta(db.Model):
    __tablename__='encuestas'
    nombre = db.Column(db.String(50),primary_key=True)
    date = db.Column(db.DateTime) #Fecha de creacion
    enlace = db.Column(db.String(80)) # Enlace para compartir con los alumnos, en lugar de generarlo varias veces. Quizas son muchos caracteres?
    confirmed_groups = db.Column(db.Boolean)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class PeerGrading(db.Model):
    __tablename__='peer_grading'
    id = db.Column(db.Integer, primary_key=True)
    #En una actividad...
    encuesta = db.Column(db.String(50), db.ForeignKey('encuestas.nombre'))
    #... un alumno...
    evaluador = db.Column(db.String(50), db.ForeignKey('estudiantes.email'))
    #... pone nota a otro alumno
    evaluado = db.Column(db.String(50), db.ForeignKey('estudiantes.email'))
    nota = db.Column(db.Float)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class GroupGrading(db.Model):
    __tablename__='group_grading'
    id = db.Column(db.Integer, primary_key=True)
    #En una actividad...
    encuesta = db.Column(db.String(50), db.ForeignKey('encuestas.nombre'))
    #... un alumno...
    evaluador = db.Column(db.String(50), db.ForeignKey('estudiantes.email'))
    #... pone nota a un grupo
    grupo = db.Column(db.String(10))
    nota = db.Column(db.Float)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

#Contenido de los ficheros excel o csv subidos por el profe
class Detalle_encuesta(db.Model):
    __tablename__='detalle_encuestas'
    #ALVARO O JORGE: LA TUPLA DE ESTUDIANTE Y ENCUESTA DEBE SER ÚNICA
    #(En la inserción de datos os debeís de asegurar de que esta tupla es única (en el caso de que te vayan a meter algún dato donde esta condición falle, sobreescribir la tupla anterior))

    #Clave primaria compuesta, no me da tiempo a probarlo, creo que se hace asi
        #Referencia a la encuesta
    encuesta = db.Column(db.String(20), db.ForeignKey('encuestas.nombre'), primary_key= True)

        #Referencia al estudiante (que tiene todo el resto de la info del csv una sola vez)
    student_mail = db.Column(db.String(50), db.ForeignKey('estudiantes.email'), primary_key = True)

    #Creo que no merece la pena hacer una tabla grupos para almacenar por tuplas (grupo, encuesta) la nota de cada grupo, sino que es mas facil calcularla cada vez
    student_group = db.Column(db.String(10))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}



### Crea filas en las tablas Encuesta, Encuesta_detalle y, si hay grupos definidos crea filas en las tablas de grading
def save_encuesta(name, filename):
    df = get_df_from_file(filename)

    encuesta = Encuesta(nombre = name, date=datetime.now(), confirmed_groups = False, enlace = "")
    db.session.add(encuesta)

    for index, row in df.iterrows():
        student_group = None

        if("group" in df.columns.values):
            student_group = df["group"][index]

        #unificar formato
        if("Username" in df.columns.values):
            df.rename(columns={'Username': 'email'}, inplace=True)
        elif("Nombre de usuario" in df.columns.values):
            df.rename(columns={'Nombre de usuario': 'email'}, inplace=True)

        encuesta_detalle = Detalle_encuesta(encuesta = name, student_mail=df["email"][index], student_group = student_group)
        db.session.add(encuesta_detalle)
    db.session.commit()

    if("group" in df.columns.values):
        create_groups(df, name)
        create_peer(df,name)


def create_groups(df, encuesta):
    df_groups = pd.DataFrame({'groups': df["group"].unique()})
    df_groups = df.merge(df_groups, how='cross')
    df_groups = df_groups[df_groups.group != df_groups.groups].copy()

    for index, row in df_groups.iterrows():
        groupGrading = GroupGrading(encuesta = encuesta, evaluador = df["email"][index], grupo = df_groups["groups"][index])
        db.session.add(groupGrading)
    db.session.commit()

def create_peer(df, encuesta):
    df_360 = df[["email", "group"]].copy()
    df_360.columns = ["email2", "group2"]
    df_360 = df.merge(df_360, how='cross')
    df_360 = df_360[(df_360.group == df_360.group2) & (df_360.email != df_360.email2)].copy()

    for index, row in df_360.iterrows():
        peerGrading = PeerGrading(encuesta = encuesta, evaluador = df["email"][index], evaluado = df["email2"][index])
        db.session.add(peerGrading)
    db.session.commit()