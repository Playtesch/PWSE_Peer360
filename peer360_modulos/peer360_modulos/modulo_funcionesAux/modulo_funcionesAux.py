import os
from flask import Blueprint, current_app
import pandas as pd
# from flask_sqlalchemy import SQLAlchemy

modulo_funcionesAux = Blueprint("modulo_funcionesAux", __name__,static_folder="static",template_folder="templates")

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'csv'}

configuration = None
import json
with open('../configuration.json') as json_file:
    configuration = json.load(json_file)

def get_configuration():
    return configuration

def allowed_file(filename):
    return '.' in filename and \
        get_extension(filename) in ALLOWED_EXTENSIONS

def get_extension(filename):
    return filename.rsplit('.', 1)[1].lower()

def swap_extension(filename, desiredExtension):
    current_extension = get_extension(filename)
    indexExtension = filename.rfind(current_extension)

    filename = filename[:indexExtension]

    filename += desiredExtension
    return filename

import csv
from csv import reader

df_global = None

def get_df_from_csv(filename):
    df_original = pd.read_csv(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

    data_frame_before = []

    with open(os.path.join(current_app.config['UPLOAD_FOLDER'], filename), 'r', encoding="utf8") as read_obj:
        csv_reader = reader(read_obj)
        for row in csv_reader:
            if (len(row)==1):
                row = csv.reader(row, quotechar='"', delimiter=',',quoting=csv.QUOTE_ALL, skipinitialspace=True)
                for l in row:
                    data_frame_before.append(l)
            else:
                data_frame_before.append(row)

    df = pd.DataFrame(data_frame_before, columns=df_original.columns)

    df = df.drop(0)

    return df


def get_df_from_file(filename):
    global df_global

    if(get_extension(filename)=="csv"):
        df_global = get_df_from_csv(filename)
    else:
        df_global = pd.read_excel(os.path.join(current_app.config['UPLOAD_FOLDER'], filename), engine='openpyxl')

    return df_global

