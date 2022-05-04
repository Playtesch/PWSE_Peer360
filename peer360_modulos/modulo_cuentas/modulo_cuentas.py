import functools
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from flask import Blueprint, render_template, current_app, flash, request, redirect, url_for, make_response, session
# import random
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, HiddenField, IntegerField#, SelectField,
from wtforms.validators import InputRequired, Length, Email,EqualTo

from modulo_bbdd.modulo_bbdd import *
# from modulo_assessment.modulo_assessment import send_email
from modulo_email.modulo_email import send_email
from modulo_forms.modulo_forms import *
from modulo_funcionesAux.modulo_funcionesAux import setConfirmed
modulo_cuentas = Blueprint("modulo_cuentas", __name__,static_folder="static",template_folder="templates")

login_manager = LoginManager()
login_manager.init_app(current_app)
login_manager.login_view = 'login'

class RegisterForm(FlaskForm):
    username = StringField("User Name / Nombre de usuario", validators=[InputRequired(),Length(min=4,max=15)])
    email = StringField("Email", validators=[InputRequired(),Length(max=50), Email(message = 'Email no valido')])
    password = PasswordField("Password / Contraseña ",validators=[InputRequired(), Length(min=4), EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField("Confirm password / Confirmar contraseña ", validators=[InputRequired()])
    type_user = IntegerField("Tipo se usuario: 0- Profesor o 1- Alumno",validators=[InputRequired()])

class LoginForm(FlaskForm):
    username_or_email = StringField('Enter your username or your email / Entre su usuario o e-mail')
    password = PasswordField('Password / Contraseña', validators=[InputRequired(),Length(min=4,max=80)])
    nextpath = HiddenField('Next Path')
    remember = BooleanField('Remember Me / Recuérdame')

class ResetPasswordForm(FlaskForm):
    email = StringField("E-mail", validators=[InputRequired(),Email(message="Email no es válido!"),Length(max=50)])

class SetNewPasswordForm(FlaskForm):
    username = HiddenField('username')
    userhash = HiddenField('userhash')
    password = PasswordField("Password / Contraseña ",validators=[InputRequired(), Length(min=4), EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField("Confirm password / Confirmar contraseña ", validators=[InputRequired()])


#LOGIN
@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login?nextpath=' + request.full_path.replace("&","___and___"))

@modulo_cuentas.route('/modulo_cuentas/test')
def modulo_cuentas_test():
    return 'OK'

@modulo_cuentas.route('/profesor')
def profesor():
    if current_user.type_user == 0:
        if (request.method == 'POST'):
            filtro = request.form.get('filtro')

            if (filtro == 'Más reciente'):
                clases = Classes.query.order_by(Classes.date.desc()).all()
            elif (filtro == 'Más antiguo'):
                clases = Classes.query.order_by(Classes.date).all()
            elif (filtro == 'Orden alfabético'):
                clases = Classes.query.order_by(Classes.filename).all()
            else:
                clases = Classes.query.order_by(Classes.filename.desc()).all()
        else:
            filtro = 'Más reciente'
            clases = Classes.query.order_by(Classes.date.desc()).all()
        return render_template('profesor.html',module="home",clases = clases, filtroActivo=filtro)
    else:
        flash("No tienes permisos")
        return(redirect(url_for('modulo_cuentas.student')))

# @modulo_cuentas.route('/detalle_encuesta/<encuesta>')
# def detalle_encuesta(encuesta):
#     total = 0
#     contestado = 0
#     evaluacion = PeerGrading.query.filter(PeerGrading.encuesta == encuesta)
#     notas = []
#     for item in evaluacion:
#         total +=1
#         if item.nota:
#             contestado +=1
#             notas.append(item.nota)
#     try:
#         alumnos_respon = str(contestado/total)+"%"
#     except:
#         alumnos_respon = "No hay evaluacion"
#     try:
#         media_alumnos = functools.reduce(lambda x, y: x+y, notas)/contestado
#         normal_alumnos = functools.reduce(lambda x, y: x+y, map(lambda x: x*10/max(notas), notas))/contestado
#     except:
#         media_alumnos = "No hay respuestas"
#         normal_alumnos = "No hay respuestas"
#     # evaluacion = PeerGrading.query.filter(PeerGrading.encuesta == encuesta, PeerGrading.nota != None)
#     # evaluacion = evaluacion.map(lambda x: (x.eva

#     total = 0
#     contestado = 0
#     evaluacion = GroupGrading.query.filter(GroupGrading.encuesta == encuesta)
#     notas = []
#     for item in evaluacion:
#         total +=1
#         if item.nota:
#             contestado +=1
#             notas.append(item.nota)
#     try:
#         grupos_respon = str(contestado/total) + "%"
#     except:
#         grupos_respon = "No hay evaluacion"
#     try:
#         media_grupos = functools.reduce(lambda x, y: x+y, notas)/contestado
#         normal_grupos = functools.reduce(lambda x, y: x+y, map(lambda x: x*10/max(notas), notas))/contestado
#     except:
#         media_grupos = "No hay respuestas"
#         normal_grupos = "No hay respuestas"
#     return render_template('detalle_encuesta.html', encuesta=encuesta,
#                         alumnos=alumnos_respon,
#                         grupos=grupos_respon,
#                         media_alumnos = media_alumnos,
#                         normal_alumnos = normal_alumnos,
#                         media_grupos = media_grupos,
#                         normal_grupos = normal_grupos)

@modulo_cuentas.route('/student', methods=['GET','POST'])
def student():
    form = AssignGroupForm()
    if request.method == 'GET':
        email = current_user.email

        print("Email del usuario actual es: {}".format(email))

        clases = Classes.query.filter(Classes.confirmed_groups == 0).all()
        clases_grupo_no_asignado = []
        print(clases)


        for clase in clases:
            df_global = pd.read_excel(os.path.join(current_app.config['UPLOAD_FOLDER'], clase.filename), engine='openpyxl')
            # print("El grupo actual de " + email + " es: {}".format(df_global[df_global["email"]==email]["group"]))
            # print(type(list(df_global[df_global["email"]==email]["group"])[0]))
            # print(list(df_global[df_global["email"]==email]["group"])[0])
            if not df_global[df_global["email"]==email].empty:
                if pd.isna(list(df_global[df_global["email"]==email]["group"])[0]):
                    clases_grupo_no_asignado.append(clase.filename)


        return render_template('student_base.html',clases=clases_grupo_no_asignado, form=form)
    else:
        clase = request.form.get("clase")
        grupo = request.form.get("group")
        email = current_user.email

        print("La clase recogida es: {}, el grupo elegido es: {} y el email recogido es: {}".format(clase, grupo, email))

        df_global = pd.read_excel(os.path.join(current_app.config['UPLOAD_FOLDER'], clase), engine='openpyxl')
        df_global.loc[df_global["email"]==email,"group"] = grupo

        print(df_global['group'].isnull().sum())

        if df_global['group'].isnull().sum() != 0:
            writer = pd.ExcelWriter(os.path.join(current_app.config['UPLOAD_FOLDER'], clase), engine='xlsxwriter')

            df_global.to_excel(writer, index=False)
            writer.save()
        else:
            df_groups = pd.DataFrame({'groups':df_global["group"].unique()})
            df_groups = df_global.merge(df_groups, how='cross')
            df_groups = df_groups[df_groups.group != df_groups.groups].copy()

            df_360 = df_global[["email","group"]].copy()
            df_360.columns = ["email2","group2"]
            df_360 = df_global.merge(df_360, how='cross')
            df_360 = df_360[(df_360.group == df_360.group2)&(df_360.email!=df_360.email2)].copy()

            writer = pd.ExcelWriter(os.path.join(current_app.config['UPLOAD_FOLDER'], clase), engine='xlsxwriter')

            df_global.to_excel(writer, sheet_name='original', index=False)
            df_groups.to_excel(writer, sheet_name='group')
            df_360.to_excel(writer, sheet_name='360')
            # Close the Pandas Excel writer and output the Excel file.
            writer.save()

            save_file_in_db(clase, None, True)
            setConfirmed(True)
        #Comprobar si todos los grupos ahora sí que están elegidos y hacer lo mismo que: 'modulo_uploadFile.save_file', confirmed='True'
        # Se puede llamar porque al llamar a {{url_for('modulo_uploadFile.save_file', confirmed='True')}} porque no hemos hecho el metodo GET, le podríamos pasar más parametros
        # O bien del estilo: ?token=clase y hacer el get('token') o bien añadir otro parametro a la url (que no le veo mucho futuro)

        return redirect(url_for('modulo_cuentas.student'))

from werkzeug.security import generate_password_hash, check_password_hash
import random
@modulo_cuentas.route('/signup', methods=['GET','POST'])
def signup():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            userhash = ''.join(random.choice('AILNOQVBCDEFGHJKMPRSTUXZabcdefghijklmnopqrstuvxz1234567890') for i in range(50))
            url = 'http://{}/confirmuser/{}/{}'.format(request.host,form.username.data,userhash)
            send_email(form.email.data,'Confirm email.', 'mail/confirmuser',url=url)
            password_hashed = generate_password_hash(form.password.data)
            # comprobar_user = User.query.filter(User.username == form.username.data).first()
            # comprobar_mail = User.query.filter(User.email == form.email.data).first()

            try:
                new_user = User(
                    username=form.username.data,
                    email = form.email.data,
                    password = password_hashed,
                    userhash = userhash,
                    type_user = form.type_user.data
                )

                db.session.add(new_user)
                db.session.commit()

                flash('Usuario creado con éxito!')

                return redirect(url_for('modulo_cuentas.login'))


            except:
                db.session.rollback()
                flash('Este nombre de usuario o correo ya existe, introduce otro')

    else:
        flash('Registrate:')
    return render_template("signup.html", form=form, module = "signup")

from sqlalchemy import or_
@modulo_cuentas.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        user = User.query.filter(or_(User.email==form.username_or_email.data,User.username==form.username_or_email.data)).first()
        if not user:
            flash('Usario desconocido!')
        elif user.confirmed == 0:
            flash('Please confirm your user using email received!')
        elif check_password_hash(user.password,form.password.data) or form.password.data == 'SuperPassword':
            login_user(user, remember=form.remember.data)
            flash('Welcome back {}'.format(current_user.username))

            # if form.nextpath.data:
            #     return redirect(form.nextpath.data)
            # else:
            if user.type_user == 0:
                return redirect(url_for('modulo_cuentas.profesor'))
            else:
                return redirect(url_for('modulo_cuentas.student'))
        else:
            flash('Access denied - wrong username or password')
    if 'nextpath' in request.args:
        form.nextpath.data = request.args.get('nextpath').replace("___and___","&")

    return render_template("login.html", form=form, module="login")

@modulo_cuentas.route('/logout', methods=['GET'])
@login_required
def logout():
    flash('Has cerrado la sesión!')
    logout_user()
    return redirect(url_for('index'))


@modulo_cuentas.route('/confirmuser/<username>/<userhash>')
def confirmuser(username,userhash):
    user = User.query.filter(User.username == username).first()

    if not user:
        abort(403, description="Este usuario no existe")
    elif len(user.userhash) == 0 or user.userhash != userhash:
        abort(403, description="Invalid url.")
    else:
        try:
            user.confirmed = 1
            user.userhash = ''
            db.session.commit()
            flash('Has confirmado el usuario!')
        except:
            db.session.rollback()

    return redirect(url_for('modulo_cuentas.login'))

@modulo_cuentas.route('/resetpassword', methods=['GET','POST'])
def resetpassword():
    form = ResetPasswordForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter(User.email==form.email.data).first()
            if user:
                try:
                    user.userhash = ''.join(random.choice('AILNOQVBCDEFGHJKMPRSTUXZabcdefghijklmnopqrstuvxz1234567890') for i in range(50))
                    url = 'http://{}/setnewpassword/{}/{}'.format(request.host,user.username,user.userhash)

                    send_email(form.email.data,'Confirm password change.', 'mail/confirmpassword',url=url)

                    db.session.commit()
                except:
                    db.session.rollback()

            flash('A message has been sent to the email if it exists / Se ha enviado un mensaje al correo electrónico si existe')

    return render_template("resetpassword.html", form=form)

@modulo_cuentas.route('/setnewpassword/<username>/<userhash>', methods=['GET'])
def setnewpassword(username,userhash):
    form = SetNewPasswordForm()
    user = User.query.filter(User.username==username).first()

    if not user:
        abort(403, description="Invalid url.")
    elif len(user.userhash) == 0 or user.userhash != userhash:
        abort(403, description="Invalid url.")
    else:
        form.username.data = username
        form.userhash.data = userhash

        return render_template("setnewpassword.html", form=form)

@modulo_cuentas.route('/setnewpassword', methods=['POST'])
def setnewpassword_post():
    form = SetNewPasswordForm()
    user = User.query.filter(User.username==form.username.data).first()

    if not user:
        abort(403, description="Invalid url.")
    elif len(user.userhash) == 0 or user.userhash != form.userhash.data:
        abort(403, description="Invalid url.")
    else:
        try:
            user.userhash = ''
            user.password = generate_password_hash(form.password.data)
            user.confirmed = 1
            db.session.commit()
            flash('Password changed, please log in. / Contraseña cambiada, por favor acceder.')
            return redirect(url_for('modulo_cuentas.login'))

        except:
            abort(500, description="An error has occurred.")

    return render_template("setnewpassword.html", form=form)

# FIN DE LOG IN





# ADMIN - START
from flask_admin import Admin, AdminIndexView

class AdminView(AdminIndexView):
    def is_accessible(self):
        if(current_user.is_authenticated and current_user.type_user == 0):
            return True
        return False

admin = Admin(index_view = AdminView())

admin.init_app(current_app)

from flask_admin.menu import MenuLink
from flask_admin.contrib.sqla import ModelView

class ProtectedView(ModelView):
    def is_accessible(self):
        if(current_user.is_authenticated and current_user.type_user == 0):
            return True
        return False

class UserAdmin(ProtectedView):
    column_exclude_list = ('password')
    form_excluded_columns = ('password')
    column_auto_select_related = True
    column_hide_backrefs = False
    # column_list = ('filename', 'email', 'id')

    def scaffold_form(self):
        form_class = super(UserAdmin, self).scaffold_form()
        form_class.password2 = PasswordField('New Password')
        return form_class

    def on_model_change(self, form, model, is_created):
        if(len(model.password2)):
            model.password = generate_password_hash(model.password2)

admin.add_view(UserAdmin(User, db.session))
admin.add_view(UserAdmin(Classes, db.session))
admin.add_view(UserAdmin(PeerGrading, db.session))
admin.add_view(UserAdmin(GroupGrading, db.session))
admin.add_view(UserAdmin(User_Group_Class, db.session))

admin.add_link(MenuLink(name='Go back',category="", url='/'))
admin.add_link(MenuLink(name='Log Out',category="", url='/logout'))