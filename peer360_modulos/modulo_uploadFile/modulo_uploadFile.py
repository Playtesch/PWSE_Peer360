import os
from flask import Blueprint, render_template, current_app, flash, request, redirect, url_for, make_response
import random

modulo_uploadFile = Blueprint("modulo_uploadFile", __name__,static_folder="static",template_folder="templates")

@modulo_uploadFile.route('/test')
def modulo_uploadFile_test():
    return 'OK'

from modulo_funcionesAux.modulo_funcionesAux import *
from modulo_bbdd.modulo_bbdd import save_file_in_db, save_groups
from modulo_forms.modulo_forms import *

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

        # group_grading = ""
        # try:
        group_grading = request.cookies.get('group_grading')
        # except:
        if not group_grading:
            group_grading = "True"

        # print("Group grading es: " + group_grading)
        # return render_template('peer360.html',module="home",df_html=df.fillna('').to_html())
        return render_template('peer360.html',module="home",df_html=df.fillna('').to_html(), group_grading=group_grading)
    elif(extension == 'csv'):
        form = AssignGroupForm()
        global df_global

        df_global = df_global.assign(group='')


        return render_template('peer360CSV.html',module="home",df_nohtml=df_global, filename=filename, form=form)


@modulo_uploadFile.route('/save_file/<string:confirmed>', methods=['GET', 'POST'])
def save_file(confirmed):
    if request.method == 'POST':
        global df_global

        form = AssignGroupForm()

        print("Antes del validate")


        filename = request.form.get('filename')

        # df_global["group"] = ['' for i in range(len(df_global.index))]

        df_global = df_global.reset_index()


        print("Al principio del validate")

        if('Nombre de usuario' in df_global.columns.values):
            peticionNombreUsuario = 'Nombre de usuario'
        else:
            peticionNombreUsuario = 'Username'

        print("Form.group es: {}".format(form.group))
        print("Form.group.data es: {}".format(form.group.data))
        print("Form.extension_mail.data es: {}".format(form.extension_mail.data))

        for index, row in df_global.iterrows():
            if eval(confirmed):
                df_global["group"]= request.form.getlist("group")
            else:
                print("Entro a vacíos")
                df_global = df_global.assign(group='')

        print("dataframe:")
        print(df_global)

        if(form.extension_mail.data):
            df_global["Nombre de usuario"] += str(form.extension_mail.data)

        excelFilename = swap_extension(filename, 'xlsx')


        print("En app, el df recogido es:\n{}".format(df_global))

        email = ""
        first_name = ""
        last_name = ""
        if 'Nombre de usuario' in df_global.columns:
            email = 'Nombre de usuario'
            first_name = "Nombre"
            last_name = "Apellidos"
        else:
            email = 'Username'
            first_name = "First Name"
            last_name = "Last Name"

        df_aux = df_global[[email]].copy()
        df_aux.columns = ["email"]
        df_aux["name"] = df_global[first_name]+" "+df_global[last_name]

        df_global[last_name] = df_aux["name"].copy()
        df_global[email] = df_aux["email"].copy()

        print("Las columnas del df antes del rename son : {}".format(df_global.columns))

        df_global = df_global.rename(columns={df_global.columns[1]: 'name'})
        df_global = df_global.rename(columns={df_global.columns[3]: 'email'})

        print("Las columnas del df formado son : {}".format(df_global.columns))

        df_global = df_global.drop(columns=[first_name])

        df_groups = pd.DataFrame({'groups':df_global["group"].unique()})
        df_groups = df_global.merge(df_groups, how='cross')
        df_groups = df_groups[df_groups.group != df_groups.groups].copy()

        df_360 = df_global[["email","group"]].copy()
        df_360.columns = ["email2","group2"]
        df_360 = df_global.merge(df_360, how='cross')
        df_360 = df_360[(df_360.group == df_360.group2)&(df_360.email!=df_360.email2)].copy()

        writer = pd.ExcelWriter(os.path.join(current_app.config['UPLOAD_FOLDER'], excelFilename), engine='xlsxwriter')

        df_global.to_excel(writer, sheet_name='original', index=False, columns=df_global.columns.values[1:])
        df_groups.to_excel(writer, sheet_name='group')
        df_360.to_excel(writer, sheet_name='360')
        # Close the Pandas Excel writer and output the Excel file.
        writer.save()

        save_file_in_db(excelFilename,confirmed)

        setConfirmed(confirmed)
        print("Hemos guardado en la base de datos el fichero")
        #DESCOMENTAR ****************************************************************************************
        save_groups(excelFilename,df_global)


        response = make_response(redirect(url_for('modulo_uploadFile.uploaded_file',
                                        filename=excelFilename)))
        response.set_cookie('filename', excelFilename)
        return response


    return render_template('index.html',module="home")
