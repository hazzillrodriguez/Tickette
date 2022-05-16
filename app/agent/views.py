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

@agent_blueprint.route('/my-tickets', methods=['GET', 'POST'])
@login_required(role='Agent')
def my_tickets():
	tickets = Ticket.query.filter(or_(Ticket.author_id==current_user.id, Ticket.owner_id==current_user.id)).order_by(desc(Ticket.created_at)).all()
	form = TicketForm()
	if form.validate_on_submit():
		number = random_numbers()
		priority = 1 # Low priority
		status = 1 # Open status

		id = current_user.id
		file = form.attachment.data
		if file is not None:
			FOLDER_ID = os.path.join(path, 'app/static/uploads/attachments/' + str(id))
			# Recursively create the paths, if the preceding path doesn't exist
			if not os.path.exists(FOLDER_ID):
				os.makedirs(FOLDER_ID)

			original_f = file.filename
			# Rename the uploaded file
			filename, ext = os.path.splitext(original_f)
			filename = uuid.uuid4().hex
			attachment = secure_filename(str(filename + ext))
			# then save it to the designated folder
			file.save(os.path.join(FOLDER_ID, attachment))
		else:
			attachment = None
			original_f = None

		ticket = Ticket(number=number, subject=form.subject.data, body=form.body.data, author_id=current_user.id, owner_id=None, category_id=int(form.category.data), priority_id=priority, status_id=status, orig_file=original_f, file_link=attachment)
		
		db.session.add(ticket)
		db.session.commit()
		flash('Ticket has been created.', 'primary')
		return redirect(url_for('agent.my_tickets'))
	return render_template('agent/my_tickets.html', form=form, tickets=tickets)

@agent_blueprint.route('/new-tickets', methods=['GET', 'POST'])
@login_required(role='Agent')
def new_tickets():
	tickets = Ticket.query.order_by(desc(Ticket.created_at)).all()
	form = TicketForm()
	if form.validate_on_submit():
		number = random_numbers()
		priority = 1 # Low priority
		status = 1 # Open status

		id = current_user.id
		file = form.attachment.data
		if file is not None:
			FOLDER_ID = os.path.join(path, 'app/static/uploads/attachments/' + str(id))
			# Recursively create the paths, if the preceding path doesn't exist
			if not os.path.exists(FOLDER_ID):
				os.makedirs(FOLDER_ID)

			original_f = file.filename
			# Rename the uploaded file
			filename, ext = os.path.splitext(original_f)
			filename = uuid.uuid4().hex
			attachment = secure_filename(str(filename + ext))
			# then save it to the designated folder
			file.save(os.path.join(FOLDER_ID, attachment))
		else:
			attachment = None
			original_f = None

		ticket = Ticket(number=number, subject=form.subject.data, body=form.body.data, author_id=current_user.id, owner_id=None, category_id=int(form.category.data), priority_id=priority, status_id=status, orig_file=original_f, file_link=attachment)
		
		db.session.add(ticket)
		db.session.commit()
		flash('Ticket has been created.', 'primary')
		return redirect(url_for('agent.new_tickets'))
	return render_template('agent/new_tickets.html', form=form, tickets=tickets)

@agent_blueprint.route('/view-ticket/<int:id>', methods=['GET', 'POST'])
@login_required(role='Agent')
def view_ticket(id):
	ticket = Ticket.query.filter_by(id=id).first()
	comments = Comment.query.filter(Comment.ticket_id==id).all()
	
	if ticket is None:
		return redirect(url_for('agent.new_tickets'))
	
	form = UpdateTicketForm(owner=ticket.owner_id, priority=ticket.priority_id, status=ticket.status_id)
	comment_form = CommentForm()
	if form.validate_on_submit():
		if not form.owner.data:
			if str(ticket.owner_id or '') != str(form.owner.data):
				db.session.add(Notification(message='unassigned ticket', receiver_id=ticket.author_id, sender_id=current_user.id, ticket_id=ticket.id, seen=False))
			ticket.owner_id = None
		else:
			if str(ticket.owner_id or '') != str(form.owner.data):
				db.session.add(Notification(message='assigned ticket', receiver_id=ticket.author_id, sender_id=current_user.id, ticket_id=ticket.id, seen=False))
			ticket.owner_id = form.owner.data
		
		if ticket.priority_id != int(form.priority.data):
			db.session.add(Notification(message='updated priority on ticket', receiver_id=ticket.author_id, sender_id=current_user.id, ticket_id=ticket.id, seen=False))
		ticket.priority_id = form.priority.data

		if ticket.status_id != int(form.status.data):
			db.session.add(Notification(message='updated status on ticket', receiver_id=ticket.author_id, sender_id=current_user.id, ticket_id=ticket.id, seen=False))
		ticket.status_id = form.status.data
		
		db.session.commit()
		flash('Ticket has been updated.', 'primary')
		return redirect(url_for('agent.view_ticket', id=id))
	return render_template('agent/view_ticket.html', form=form, comment_form=comment_form, ticket=ticket, comments=comments)