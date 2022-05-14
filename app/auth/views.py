from flask import Blueprint, render_template as _render, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user

from app.auth.forms import LoginForm, SignupForm, ForgotPasswordForm, ResetPasswordForm
from app.utils.redirect_url_endpoint import url_destination
from app.utils.reset_password import send_reset_link
from app.models import User
from app.exts import db

from werkzeug.security import check_password_hash, generate_password_hash
import datetime

auth_blueprint = Blueprint('auth', __name__)

# Pass variable to all templates
def render_template(*args, **kwargs):
	year = datetime.date.today().year
	return _render(*args, **kwargs, year=year)

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
	# If user is already authenticated redirect to designated page
	if current_user.is_authenticated and current_user.role == 'Administrator':
		return url_destination(fallback=url_for('admin.dashboard'))
	elif current_user.is_authenticated and current_user.role == 'Agent':
		return url_destination(fallback=url_for('agent.dashboard'))
	elif current_user.is_authenticated and current_user.role == 'Customer':
		return url_destination(fallback=url_for('customer.dashboard'))

	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and check_password_hash(user.password, form.password.data) and user.role == 'Administrator':
			login_user(user, remember=form.remember.data)
			return url_destination(fallback=url_for('admin.dashboard'))
		elif user and check_password_hash(user.password, form.password.data) and user.role == 'Agent':
			login_user(user, remember=form.remember.data)
			return url_destination(fallback=url_for('agent.dashboard'))
		elif user and check_password_hash(user.password, form.password.data) and user.role == 'Customer':
			login_user(user, remember=form.remember.data)
			return url_destination(fallback=url_for('customer.dashboard'))
		else:
			flash('Your email or password is incorrect, please try again!', 'danger')
	return render_template('auth/login.html', form=form)

@auth_blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
	if current_user.is_authenticated and current_user.role == 'Administrator':
		return url_destination(fallback=url_for('admin.dashboard'))
	elif current_user.is_authenticated and current_user.role == 'Agent':
		return url_destination(fallback=url_for('agent.dashboard'))
	elif current_user.is_authenticated and current_user.role == 'Customer':
		return url_destination(fallback=url_for('customer.dashboard'))
		
	form = SignupForm()
	if form.validate_on_submit():
		hashed_password = generate_password_hash(form.password.data)
		role = 'Customer'
		image = 'default-profile.png'
		user = User(
			name=form.name.data,
			email=form.email.data,
			password=hashed_password,
			role=role,
			image=image
		)
		db.session.add(user)
		db.session.commit()

		flash('Your account has been created.', 'primary')
		return redirect(url_for('auth.login'))
	return render_template('auth/signup.html', form=form)

@auth_blueprint.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('auth.login'))

@auth_blueprint.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
	if current_user.is_authenticated and current_user.role == 'Administrator':
		return url_destination(fallback=url_for('admin.dashboard'))
	elif current_user.is_authenticated and current_user.role == 'Agent':
		return url_destination(fallback=url_for('agent.dashboard'))
	elif current_user.is_authenticated and current_user.role == 'Customer':
		return url_destination(fallback=url_for('customer.dashboard'))

	form = ForgotPasswordForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		send_reset_link(user)
		flash('Check your email for a link to reset your password.', 'primary')
		return redirect(url_for('auth.login'))
	return render_template('auth/forgot_password.html', form=form)

@auth_blueprint.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
	if current_user.is_authenticated and current_user.role == 'Administrator':
		return url_destination(fallback=url_for('admin.dashboard'))
	elif current_user.is_authenticated and current_user.role == 'Agent':
		return url_destination(fallback=url_for('agent.dashboard'))
	elif current_user.is_authenticated and current_user.role == 'Customer':
		return url_destination(fallback=url_for('customer.dashboard'))

	user = User.verify_reset_token(token)
	if user is None:
		flash('Invalid or expired token, please try again!', 'warning')
		return redirect(url_for('auth.forgot_password'))

	form = ResetPasswordForm()
	if form.validate_on_submit():
		hashed_password = generate_password_hash(form.password.data)
		user.password = hashed_password
		db.session.commit()

		flash('Your password has been updated.', 'primary')
		return redirect(url_for('auth.login'))
	return render_template('auth/reset_password.html', form=form)