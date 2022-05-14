from flask import render_template
from flask_mail import Message
from app.exts import mail
import os

def send_reset_link(user):
	token = user.get_reset_token()
	message = Message(
		'[Tickette] Reset Password',
		sender=os.environ.get('MAIL_USERNAME'),
		recipients=[user.email]
	)
	message.body = render_template('email/reset_password.txt', name=user.name, token=token)
	message.html = render_template('email/reset_password.html', name=user.name, token=token)
	mail.send(message)