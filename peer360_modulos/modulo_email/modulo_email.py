import os
from flask import Blueprint, request, send_file, render_template, make_response, url_for, redirect, current_app
from flask_mail import Mail, Message

modulo_email = Blueprint("modulo_email", __name__,static_folder="static",template_folder="templates")

mail = Mail(current_app)

def send_email(to, subject, template, url, **kwargs):
    print("Url: {} ".format(url))
    msg = Message(current_app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject, sender=current_app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs, url=url)
    msg.html = render_template(template + '.html', **kwargs, url=url)
    # flash("send_email: {}".format(url))
    print("El email va a ser:{}".format(msg))
    print("El body va a ser:{}".format(msg.body))
    print("El html va a ser:{}".format(msg.html))
    mail.send(msg)
