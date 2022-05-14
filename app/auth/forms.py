from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, BooleanField
from wtforms.validators import DataRequired, ValidationError, Email, Length
from app.models import User

class SignupForm(FlaskForm):
	name = StringField('Name',
		validators=[DataRequired(), Length(min=4, max=32)])
	email = EmailField('Email',
		validators=[DataRequired(), Email(), Length(min=6, max=64)])
	password = PasswordField('Password',
		validators=[DataRequired(), Length(min=6, max=32)])
	agree = BooleanField('I agree to the Terms and Conditions',
		validators=[DataRequired()])

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('This e-mail address is already taken')

class LoginForm(FlaskForm):
	email = EmailField('Email',
		validators=[DataRequired(), Email()])
	password = PasswordField('Password',
		validators=[DataRequired()])
	remember = BooleanField('Remember me')

class ForgotPasswordForm(FlaskForm):
	email = EmailField('Email',
		validators=[DataRequired(), Email()])

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is None:
			raise ValidationError('This e-mail address doesn\'t exist')

class ResetPasswordForm(FlaskForm):
	password = PasswordField('New Password',
		validators=[DataRequired(), Length(min=6, max=32)])