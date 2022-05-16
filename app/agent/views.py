from flask import Blueprint, current_app, render_template as _render, send_file, redirect, request, url_for, flash
from flask_login import current_user

from app.admin.forms import TicketForm, UpdateTicketForm, CommentForm, CategoryForm, PriorityForm, UserForm, UpdateRoleForm, ChangeProfileForm, ChangePasswordForm
from app.models import User, Ticket, Category, Priority, Status, Comment, Notification

from app.utils.generate_digits import random_numbers
from app.utils.authorized_role import login_required
from app.exts import db

from werkzeug.utils import secure_filename

from sqlalchemy import desc
from sqlalchemy import or_

from werkzeug.security import generate_password_hash

import datetime
import shutil
import uuid
import os

agent_blueprint = Blueprint('agent', __name__)
path = os.getcwd()

# Pass variable to all templates
def render_template(*args, **kwargs):
	notifications = Notification.query.filter(Notification.receiver_id==current_user.id).filter(Notification.seen==False).order_by(desc(Notification.created_at)).all()
	year = datetime.date.today().year
	return _render(*args, **kwargs, notifications=notifications, year=year)

@agent_blueprint.route('/dashboard')
@login_required(role='Agent')
def dashboard():
	id = current_user.id
	open = Ticket.query.filter_by(owner_id=id).filter_by(status_id=1).all()
	solved = Ticket.query.filter_by(owner_id=id).filter_by(status_id=2).all()
	pending = Ticket.query.filter_by(owner_id=id).filter_by(status_id=3).all()
	closed = Ticket.query.filter_by(owner_id=id).filter_by(status_id=4).all()
	
	return render_template('agent/dashboard.html', open=open, solved=solved, pending=pending, closed=closed)