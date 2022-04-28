import os
from flask import Blueprint, render_template, current_app, flash, request, redirect, url_for, make_response
import random

modulo_uploadFile = Blueprint("modulo_uploadFile", __name__,static_folder="static",template_folder="templates")

from modulo_funcionesAux.modulo_funcionesAux import *
from modulo_bbdd.modulo_bbdd import save_file_in_db, save_groups

df_global = None

@modulo_uploadFile.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            global df_global
            if get_extension(file.filename) == 'xlsx':
    #            filename = secure_filename(file.filename)
                filename = "F"+''.join(random.choice('AILNOQVBCDEFGHJKMPRSTUXZabcdefghijklmnopqrstuvxz1234567890') for i in range(10))+".xlsx"
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

                df_global = get_df_from_file(filename)


                print("En app, el df recogido es:\n{}".format(df_global))
                df_groups = pd.DataFrame({'groups':df_global["group"].unique()})

                df_groups = df_global.merge(df_groups, how='cross')
                df_groups = df_groups[df_groups.group != df_groups.groups].copy()
                df_360 = df_global[["email","group"]].copy()
                df_360.columns = ["email2","group2"]
                df_360 = df_global.merge(df_360, how='cross')
                df_360 = df_360[(df_360.group == df_360.group2)&(df_360.email!=df_360.email2)].copy()

                writer = pd.ExcelWriter(os.path.join(current_app.config['UPLOAD_FOLDER'], filename), engine='xlsxwriter')

                df_global.to_excel(writer, sheet_name='original', index=False)
                df_groups.to_excel(writer, sheet_name='group')
                df_360.to_excel(writer, sheet_name='360')
                # Close the Pandas Excel writer and output the Excel file.
                writer.save()

                save_file_in_db(filename)

                # save_groups(filename)

                response = make_response(redirect(url_for('modulo_uploadFile.uploaded_file',
                                        filename=filename)))
                response.set_cookie('filename', filename)
                return response

            elif get_extension(file.filename) == 'csv':

                filename = "F"+''.join(random.choice('AILNOQVBCDEFGHJKMPRSTUXZabcdefghijklmnopqrstuvxz1234567890') for i in range(10))+".csv"
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

                df_global = get_df_from_file(filename)

                response = make_response(redirect(url_for('modulo_uploadFile.uploaded_file',
                                        filename=filename)))
                response.set_cookie('filename', filename)
                return response



    return render_template('upload_file.html',module="upload_file",cookie=True)

#from flask import send_from_directory

# import pandas as pd
@modulo_uploadFile.route('/uploads/<filename>')
def uploaded_file(filename):

    extension = get_extension(filename)

    if(extension == 'xlsx'):
        df = pd.read_excel(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        # return render_template('peer360.html',module="home",df_html=df.fillna('').to_html())
        return render_template('peer360.html',module="home",df_html=df.fillna('').to_html())
    elif(extension == 'csv'):
        global df_global

        df_global["group"] = ['' for i in range(len(df_global.index))]


        return render_template('peer360CSV.html',module="home",df_nohtml=df_global, filename=filename)


@modulo_uploadFile.route('/save_file', methods=['GET', 'POST'])
def save_file():
    if request.method == 'POST':

        global df_global

        filename = request.form.get('filename')

        # df_global["group"] = ['' for i in range(len(df_global.index))]

        df_global = df_global.reset_index()


        if('Nombre de usuario' in df_global.columns.values):
            peticionNombreUsuario = 'Nombre de usuario'
        else:
            peticionNombreUsuario = 'Username'

        for index, row in df_global.iterrows():
            df_global["group"][index] = request.form.get(row[peticionNombreUsuario])

        print("dataframe:")
        print(df_global)

        if(request.form.get("extensionCorreo")):
            for index, row in df_global.iterrows():
                df_global["Nombre de usuario"][index] += request.form.get("extensionCorreo")

        excelFilename = swap_extension(filename, 'xlsx')

        writer = pd.ExcelWriter(os.path.join(current_app.config['UPLOAD_FOLDER'], excelFilename), engine='xlsxwriter')
        df_global.to_excel(writer, index=False, columns=df_global.columns.values[1:])
        writer.save()

        save_file_in_db(excelFilename)

        #DESCOMENTAR ****************************************************************************************
        # save_groups(excelFilename)

        response = make_response(redirect(url_for('modulo_uploadFile.uploaded_file',
                                        filename=excelFilename)))
        response.set_cookie('filename', excelFilename)
        return response


    return render_template('index.html',module="home")