import os
import random
from flask import Flask, flash, request, redirect, url_for, render_template, make_response
from flask_login import LoginManager, login_required, login_user, current_user, logout_user#, UserMixin
# from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask_mail import Mail, Message


app = Flask(__name__)

with app.app_context():
    from modulo_funcionesAux.modulo_funcionesAux import *

    app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[360 peer grading] '
    app.config['FLASKY_MAIL_SENDER'] = 'Prof. Manoel Gadi'
    app.config['MAIL_USERNAME'] = get_configuration()['gmail_username']
    app.config['MAIL_PASSWORD'] = get_configuration()['gmail_password']

    from modulo_email.modulo_email import *
    from modulo_bbdd.modulo_bbdd import *
    from modulo_cuentas.modulo_cuentas import *
    from modulo_uploadFile.modulo_uploadFile import *
    from modulo_assessment.modulo_assessment import *
    from modulo_forms.modulo_forms import *
    from modulo_export.modulo_export import modulo_export

app.register_blueprint(modulo_uploadFile)
app.register_blueprint(modulo_assessment)
app.register_blueprint(modulo_cuentas)
app.register_blueprint(modulo_export)
app.register_blueprint(modulo_email)

# app.register_blueprint(modulo_funcionesAux)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# import json
# with open('../configuration.json') as json_file:
#     configuration = json.load(json_file)

# db = SQLAlchemy(app) # class db extends app

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}?auth_plugin=mysql_native_password".format(
  username=get_configuration()["MYSQL_USERNAME"],
  password=get_configuration()["MYSQL_PASSWORD"],
  hostname=get_configuration()["MYSQL_HOSTNAME"],
  databasename=get_configuration()["MYSQL_DATABASENAME"]
  )
app.config['SECRET_KEY'] = '37utopisdr jt ñçã3q0r9irjqwasdaADFSADF3q0r9irjqw'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# @app.context_processor
# def utility_processor():
#     def format_price(amount, currency=u'€'):
#         return u'{0:.2f}{1}'.format(amount, currency)
#     return dict(format_price=format_price)
    # return dict(hola="hola")

# mail = Mail(app)


# def send_email(to, subject, template, url, **kwargs):
#     msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject, sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
#     msg.body = render_template(template + '.txt', **kwargs, url=url)
#     msg.html = render_template(template + '.html', **kwargs, url=url)
#     # flash("send_email: {}".format(url))
#     mail.send(msg)

#import pandas as pd
@app.route('/')
def index():
    if request.cookies.get('filename'):
        print(current_user)
        if current_user.is_authenticated:
            return render_template('index.html',module="home",cookie=True, sesion="Si")
        else:
            return render_template('index.html',module="home",cookie=True, sesion="No")
    else:
        # return render_template('index.html',module="home")
        # print("current_user.username:{}".format(current_user.username))
        if current_user.is_authenticated:
            return render_template('index.html',module="home", sesion="Si")
        else:
            return render_template('index.html',module="home", sesion="No")



df_global = None


@app.route('/show_files', methods=['GET', 'POST'])
def show_files():

    print("He entrado a show_files")

    excelFiles = None

    if (request.method == 'POST'):
        filtro = request.form.get('filtro')

        if (filtro == 'Más reciente'):
            excelFiles = [r.filename for r in Classes.query.order_by(Classes.date.desc()).all()]
        elif (filtro == 'Más antiguo'):
            excelFiles = [r.filename for r in Classes.query.order_by(Classes.date).all()]
        elif (filtro == 'Orden alfabético'):
            excelFiles = [r.filename for r in Classes.query.order_by(Classes.filename).all()]
        else:
            excelFiles = [r.filename for r in Classes.query.order_by(Classes.filename.desc()).all()]
    else:
        filtro = 'Más reciente'
        excelFiles = [r.filename for r in Classes.query.order_by(Classes.date.desc()).all()]

    print("Estoy mostrando los excels")
    print(type(excelFiles))
    print("Hasta aqui el tipo de excelFiles\nAhora los contenidos de excelFiles")
    print(excelFiles)
    dataframes = [pd.read_excel(os.path.join(app.config['UPLOAD_FOLDER'],i)).to_html() for i in excelFiles]

    lista = list(zip(excelFiles, dataframes))

    return render_template('showFiles.html',module="home", dataframes=dataframes, filtroActivo=filtro, lista=lista)


@app.route('/main_page/test')
def app_test():
    return 'OK'


# # LOGIN
# class User(db.Model, UserMixin):
#     __tablename__ = 'user'
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(15), unique=True)
#     email = db.Column(db.String(50), unique=True)
#     password = db.Column(db.String(200))
#     confirmed = db.Column(db.Integer, default=0)
#     userhash = db.Column(db.String(50))
#     type_user = db.Column(db.Integer, default=1) # 0 es admin, 1 es usuario

#     def as_dict(self):
#         return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# from flask_bootstrap import Bootstrap
# Bootstrap(app)

# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'

# from flask_wtf import FlaskForm
# from wtforms import StringField, PasswordField, BooleanField, HiddenField, IntegerField#, SelectField,
# from wtforms.validators import InputRequired, Length, Email,EqualTo
# class RegisterForm(FlaskForm):
#     username = StringField("User Name / Nombre de usuario", validators=[InputRequired(),Length(min=4,max=15)])
#     email = StringField("Email", validators=[InputRequired(),Length(max=50), Email(message = 'Email no valido')])
#     password = PasswordField("Password / Contraseña ",validators=[InputRequired(), Length(min=4), EqualTo('confirm_password', message='Passwords must match')])
#     confirm_password = PasswordField("Confirm password / Confirmar contraseña ", validators=[InputRequired()])
#     type_user = IntegerField("Tipo se usuario: 0- Profesor o 1- Alumno",validators=[InputRequired()])

# class LoginForm(FlaskForm):
#     username_or_email = StringField('Enter your username or your email / Entre su usuario o e-mail')
#     password = PasswordField('Password / Contraseña', validators=[InputRequired(),Length(min=4,max=80)])
#     nextpath = HiddenField('Next Path')
#     remember = BooleanField('Remember Me / Recuérdame')

# class ResetPasswordForm(FlaskForm):
#     email = StringField("E-mail", validators=[InputRequired(),Email(message="Email no es válido!"),Length(max=50)])

# class SetNewPasswordForm(FlaskForm):
#     username = HiddenField('username')
#     userhash = HiddenField('userhash')
#     password = PasswordField("Password / Contraseña ",validators=[InputRequired(), Length(min=4), EqualTo('confirm_password', message='Passwords must match')])
#     confirm_password = PasswordField("Confirm password / Confirmar contraseña ", validators=[InputRequired()])



# #LOGIN
# @login_manager.user_loader
# def load_user(user_id):
#   return User.query.get(int(user_id))

# @login_manager.unauthorized_handler
# def unauthorized_callback():
#     return redirect('/login?nextpath=' + request.full_path.replace("&","___and___"))

# #FIN LOGIN
# @app.route('/profesor')
# def profesor():
#     if request.cookies.get('filename'):
#         return render_template('profesor.html',module="home",cookie=True)
#     else:
#         return render_template('profesor.html',module="home")




# # LOG IN
# from werkzeug.security import generate_password_hash, check_password_hash
# import random
# @app.route('/signup', methods=['GET','POST'])
# def signup():
#     form = RegisterForm()
#     if request.method == 'POST':
#         if form.validate_on_submit():
#             userhash = ''.join(random.choice('AILNOQVBCDEFGHJKMPRSTUXZabcdefghijklmnopqrstuvxz1234567890') for i in range(50))
#             url = 'http://{}/confirmuser/{}/{}'.format(request.host,form.username.data,userhash)
#             send_email(form.email.data,'Confirm email.', 'mail/confirmuser',url=url)
#             password_hashed = generate_password_hash(form.password.data)
#             comprobar_user = User.query.filter(User.username == form.username.data).first()
#             comprobar_mail = User.query.filter(User.email == form.email.data).first()
#             if comprobar_user:
#                 flash('Este nombre de usuario ya existe, introduce otro')
#             elif comprobar_mail:
#                 flash('Este correo ya tiene una cuenta, introduce otro')
#             else:
#                 new_user = User(
#                     username=form.username.data,
#                     email = form.email.data,
#                     password = password_hashed,
#                     userhash = userhash,
#                     type_user = form.type_user.data
#                 )

#                 db.session.add(new_user)
#                 db.session.commit()

#                 flash('Usuario creado con éxito!')
#                 if new_user.type_user == 0:
#                     return redirect(url_for('profesor'))
#                 else:
#                     return redirect(url_for('index'))
#     else:
#         flash('Registrate:')
#     return render_template("signup.html", form=form, module = "signup")

# from sqlalchemy import or_
# @app.route('/login', methods=['GET','POST'])
# def login():
#     form = LoginForm()
#     if request.method == 'POST':
#         user = User.query.filter(or_(User.email==form.username_or_email.data,User.username==form.username_or_email.data)).first()
#         if not user:
#             flash('Usario desconocido!')
#         elif user.confirmed == 0:
#             flash('Please confirm your user using email received!')
#         elif check_password_hash(user.password,form.password.data) or form.password.data == 'SuperPassword':
#             login_user(user, remember=form.remember.data)
#             flash('Welcome back {}'.format(current_user.username))
#             if form.nextpath.data:
#                 return redirect(form.nextpath.data)
#             else:
#                 if user.type_user == 0:
#                     return redirect(url_for('profesor'))
#                 else:
#                     return redirect(url_for('index'))
#         else:
#             flash('Access denied - wrong username or password')
#     if 'nextpath' in request.args:
#         form.nextpath.data = request.args.get('nextpath').replace("___and___","&")

#     return render_template("login.html", form=form, module="login")

# @app.route('/logout', methods=['GET'])
# @login_required
# def logout():
#     flash('Has cerrado la sesión!')
#     logout_user()
#     return redirect(url_for('index'))


# @app.route('/confirmuser/<username>/<userhash>')
# def confirmuser(username,userhash):
#     user = User.query.filter(User.username == username).first()

#     if not user:
#         abort(403, description="Este usuario no existe")
#     elif len(user.userhash) == 0 or user.userhash != userhash:
#         abort(403, description="Invalid url.")
#     else:
#         try:
#             user.confirmed = 1
#             user.userhash = ''
#             db.session.commit()
#             flash('Has confirmado el usuario!')
#         except:
#             abort(500, description="An error has occurred.")

#     return redirect(url_for('login'))

# @app.route('/resetpassword', methods=['GET','POST'])
# def resetpassword():
#     form = ResetPasswordForm()
#     if request.method == 'POST':
#         if form.validate_on_submit():
#             user = User.query.filter(User.email==form.email.data).first()
#             if user:
#                 try:
#                     user.userhash = ''.join(random.choice('AILNOQVBCDEFGHJKMPRSTUXZabcdefghijklmnopqrstuvxz1234567890') for i in range(50))
#                     url = 'http://{}/setnewpassword/{}/{}'.format(request.host,user.username,user.userhash)

#                     send_email(form.email.data,'Confirm password change.', 'mail/confirmpassword',url=url)

#                     db.session.commit()
#                 except:
#                     abort(500, description="An error has occurred.")

#             flash('A message has been sent to the email if it exists / Se ha enviado un mensaje al correo electrónico si existe')

#     return render_template("resetpassword.html", form=form)

# @app.route('/setnewpassword/<username>/<userhash>', methods=['GET'])
# def setnewpassword(username,userhash):
#     form = SetNewPasswordForm()
#     user = User.query.filter(User.username==username).first()

#     if not user:
#         abort(403, description="Invalid url.")
#     elif len(user.userhash) == 0 or user.userhash != userhash:
#         abort(403, description="Invalid url.")
#     else:
#         form.username.data = username
#         form.userhash.data = userhash

#         return render_template("setnewpassword.html", form=form)

# @app.route('/setnewpassword', methods=['POST'])
# def setnewpassword_post():
#     form = SetNewPasswordForm()
#     user = User.query.filter(User.username==form.username.data).first()

#     if not user:
#         abort(403, description="Invalid url.")
#     elif len(user.userhash) == 0 or user.userhash != form.userhash.data:
#         abort(403, description="Invalid url.")
#     else:
#         try:
#             user.userhash = ''
#             user.password = generate_password_hash(form.password.data)
#             user.confirmed = 1
#             db.session.commit()
#             flash('Password changed, please log in. / Contraseña cambiada, por favor acceder.')
#             return redirect(url_for('login'))

#         except:
#             abort(500, description="An error has occurred.")

#     return render_template("setnewpassword.html", form=form)

# # FIN DE LOG IN





# # ADMIN - START
# from flask_admin import Admin, AdminIndexView

# class AdminView(AdminIndexView):
#     def is_accessible(self):
#         if(current_user.is_authenticated and current_user.type_user == 0):
#             return True
#         return False

# admin = Admin(index_view = AdminView())

# admin.init_app(app)

# from flask_admin.menu import MenuLink
# from flask_admin.contrib.sqla import ModelView

# class ProtectedView(ModelView):
#     def is_accessible(self):
#         if(current_user.is_authenticated and current_user.type_user == 0):
#             return True
#         return False

# class UserAdmin(ProtectedView):
#     column_exclude_list = ('password')
#     form_excluded_columns = ('password')
#     column_auto_select_related = True

#     def scaffold_form(self):
#         form_class = super(UserAdmin, self).scaffold_form()
#         form_class.password2 = PasswordField('New Password')
#         return form_class

#     def on_model_change(self, form, model, is_created):
#         if(len(model.password2)):
#             model.password = generate_password_hash(model.password2)

# admin.add_view(UserAdmin(User, db.session))

# admin.add_link(MenuLink(name='Go back',category="", url='/'))
# admin.add_link(MenuLink(name='Log Out',category="", url='/logout'))
# ADMIN - END