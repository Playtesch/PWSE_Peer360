import os
from flask import Blueprint, current_app
import pandas as pd
from flask_bootstrap import Bootstrap
Bootstrap(current_app)
# from flask_sqlalchemy import SQLAlchemy

modulo_forms = Blueprint("modulo_forms", __name__,static_folder="static",template_folder="templates")

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, HiddenField, SelectField
from wtforms.validators import InputRequired, Length, Email,EqualTo

class AssignGroupForm(FlaskForm):
    extension_mail = StringField('Introduzca la extension del email ', validators=[InputRequired(),Email(message="Email no es válido!"),Length(max=50)])
    group = SelectField('Group/Grupo', choices=[('', '--'), ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
