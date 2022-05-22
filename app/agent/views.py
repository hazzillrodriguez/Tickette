from flask import Blueprint, current_app, render_template as _render, send_file, redirect, request, url_for, flash
from flask_login import current_user

from app.agent.forms import TicketForm, UpdateTicketForm, CommentForm, CategoryForm, PriorityForm, ChangeProfileForm, ChangePasswordForm
from app.models import User, Ticket, Category, Priority, Status, Comment, Notification

from app.utils.generate_digits import random_numbers
from app.utils.authorized_role import login_required
from app.exts import db

from werkzeug.utils import secure_filename

from sqlalchemy import desc
from sqlalchemy import or_

from werkzeug.security import generate_password_hash

import datetime
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
	open = Ticket.query.filter(or_(Ticket.author_id==id, Ticket.owner_id==id)).filter_by(status_id=1).all()
	solved = Ticket.query.filter(or_(Ticket.author_id==id, Ticket.owner_id==id)).filter_by(status_id=2).all()
	pending = Ticket.query.filter(or_(Ticket.author_id==id, Ticket.owner_id==id)).filter_by(status_id=3).all()
	closed = Ticket.query.filter(or_(Ticket.author_id==id, Ticket.owner_id==id)).filter_by(status_id=4).all()
	
	return render_template('agent/dashboard.html', open=open, solved=solved, pending=pending, closed=closed)

@agent_blueprint.route('/my-tickets', methods=['GET'])
@login_required(role='Agent')
def my_tickets():
	tickets = Ticket.query.filter(or_(Ticket.author_id==current_user.id, Ticket.owner_id==current_user.id)).order_by(desc(Ticket.created_at)).all()
	form = TicketForm()
	return render_template('agent/my_tickets.html', form=form, tickets=tickets)

@agent_blueprint.route('/new-tickets', methods=['GET'])
@login_required(role='Agent')
def new_tickets():
	tickets = Ticket.query.order_by(desc(Ticket.created_at)).all()
	form = TicketForm()
	return render_template('agent/new_tickets.html', form=form, tickets=tickets)

@agent_blueprint.route('/create-ticket', methods=['GET', 'POST'])
@login_required(role='Agent')
def create_ticket():
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

@agent_blueprint.route('/view-ticket/<int:id>', methods=['GET', 'POST'])
@login_required(role='Agent')
def view_ticket(id):
	ticket = Ticket.query.filter_by(id=id).first()
	comments = Comment.query.filter(Comment.ticket_id==id).all()
	
	if not ticket:
		return redirect(url_for('agent.new_tickets'))
	
	form = UpdateTicketForm(owner=ticket.owner_id, priority=ticket.priority_id, status=ticket.status_id)
	comment_form = CommentForm()
	if form.validate_on_submit():
		if not form.owner.data:
			if str(ticket.owner_id or '') != str(form.owner.data) and ticket.author_id != current_user.id:
				Notification.send_notification(message='unassigned ticket', receiver_id=ticket.author_id, sender_id=current_user.id, ticket_id=ticket.id, seen=False)
			if str(ticket.owner_id or '') != str(form.owner.data) and ticket.author_id == current_user.id:
				Notification.send_notification(message='unassigned ticket', receiver_id=ticket.owner_id, sender_id=current_user.id, ticket_id=ticket.id, seen=False)
			ticket.owner_id = None
		else:
			if str(ticket.owner_id or '') != str(form.owner.data) and ticket.author_id != current_user.id:
				Notification.send_notification(message='assigned ticket', receiver_id=ticket.author_id, sender_id=current_user.id, ticket_id=ticket.id, seen=False)
				Notification.send_notification(message='assigned ticket', receiver_id=form.owner.data, sender_id=current_user.id, ticket_id=ticket.id, seen=False)
			if str(ticket.owner_id or '') != str(form.owner.data) and ticket.author_id == current_user.id:
				Notification.send_notification(message='assigned ticket', receiver_id=form.owner.data, sender_id=current_user.id, ticket_id=ticket.id, seen=False)
			ticket.owner_id = form.owner.data
		
		if ticket.priority_id != int(form.priority.data) and ticket.author_id != current_user.id:
			Notification.send_notification(message='updated priority on ticket', receiver_id=ticket.author_id, sender_id=current_user.id, ticket_id=ticket.id, seen=False)
		ticket.priority_id = form.priority.data

		if ticket.status_id != int(form.status.data) and ticket.author_id != current_user.id:
			Notification.send_notification(message='updated status on ticket', receiver_id=ticket.author_id, sender_id=current_user.id, ticket_id=ticket.id, seen=False)
		ticket.status_id = form.status.data
		
		db.session.commit()
		flash('Ticket has been updated.', 'primary')
		return redirect(url_for('agent.view_ticket', id=id))
	return render_template('agent/view_ticket.html', form=form, comment_form=comment_form, ticket=ticket, comments=comments)

@agent_blueprint.route('/comment-ticket/<int:id>', methods=['GET', 'POST'])
@login_required(role='Agent')
def comment_ticket(id):
	ticket_id = Ticket.query.get_or_404(id)
	comment_form = CommentForm()
	if comment_form.validate_on_submit():
		author_id = ticket_id.author_id
		owner_id = ticket_id.owner_id
		comment = comment_form.comment.data

		message = 'commented on ticket'
		# Send notification to the author and owner, if the ticket is not mine and is not assigned to me
		if author_id != current_user.id and owner_id != current_user.id and owner_id is not None:
			Notification.send_notification(message=message, receiver_id=author_id, sender_id=current_user.id, ticket_id=ticket_id.id, seen=False)
			Notification.send_notification(message=message, receiver_id=owner_id, sender_id=current_user.id, ticket_id=ticket_id.id, seen=False)
		# Send notification to the author, if the ticket is not mine
		elif author_id != current_user.id:
			Notification.send_notification(message=message, receiver_id=author_id, sender_id=current_user.id, ticket_id=ticket_id.id, seen=False)
		# Send notification to the owner, if the ticket is mine and is not assigned to me
		if author_id == current_user.id and owner_id != current_user.id and owner_id is not None:
			Notification.send_notification(message=message, receiver_id=owner_id, sender_id=current_user.id, ticket_id=ticket_id.id, seen=False)

		db.session.add(Comment(comment=comment, author_id=current_user.id, ticket_id=ticket_id.id))
		db.session.commit()
		flash('Your comment has been posted.', 'primary')
		return redirect(url_for('agent.view_ticket', id=id))
	return render_template('agent/view_ticket.html', comment_form=comment_form)

@agent_blueprint.route('/ticket/delete/<int:uid>/<int:tid>', methods=['GET', 'POST'])
@login_required(role='Agent')
def delete_ticket(uid, tid):
	ticket_id = Ticket.query.get_or_404(tid)
	if request.method == 'POST':
		if ticket_id.file_link:
			FOLDER_ID = os.path.join(path, 'app/static/uploads/attachments/' + str(uid))
			os.remove(os.path.join(FOLDER_ID, ticket_id.file_link))

		db.session.delete(ticket_id)
		db.session.commit()
		flash('Ticket has been deleted.', 'primary')
		return redirect(url_for('agent.new_tickets'))
	return redirect(url_for('agent.view_ticket', id=tid))

@agent_blueprint.route('/download/attachment/<int:id>/<filename>')
def download_attachment(id, filename):
	FOLDER_ID = os.path.join(path, 'app/static/uploads/attachments/' + str(id))
	location = os.path.join(FOLDER_ID, filename)
	return send_file(location, as_attachment=True)

@agent_blueprint.route('/categories', methods=['GET', 'POST'])
@login_required(role='Agent')
def category():
	categories = Category.query.all()
	form = CategoryForm()
	if form.validate_on_submit():
		category = Category(category=form.category.data)
		db.session.add(category)
		db.session.commit()
		flash('Category has been created.', 'primary')
		return redirect(url_for('agent.category'))
	return render_template('agent/category.html', form=form, categories=categories)

@agent_blueprint.route('/category/update/<int:id>', methods=['GET', 'POST'])
@login_required(role='Agent')
def update_category(id):
	category_id = Category.query.get_or_404(id)
	form = CategoryForm()
	if form.validate_on_submit():
		category_id.category = form.category.data
		db.session.commit()
		flash('Category has been updated.', 'primary')
		return redirect(url_for('agent.category'))
	return render_template('agent/category.html', form=form)

@agent_blueprint.route('/category/delete/<int:id>', methods=['GET', 'POST'])
@login_required(role='Agent')
def delete_category(id):
	category_id = Category.query.get_or_404(id)
	if request.method == 'POST':
		db.session.delete(category_id)
		db.session.commit()
		flash('Category has been deleted.', 'primary')
		return redirect(url_for('agent.category'))
	return redirect(url_for('agent.category'))

@agent_blueprint.route('/priorities', methods=['GET', 'POST'])
@login_required(role='Agent')
def priority():
	priorities = Priority.query.all()
	form = PriorityForm()
	if form.validate_on_submit():
		priority = Priority(priority=form.priority.data)
		db.session.add(priority)
		db.session.commit()
		flash('Priority has been created.', 'primary')
		return redirect(url_for('agent.priority'))
	return render_template('agent/priority.html', form=form, priorities=priorities)

@agent_blueprint.route('/priority/update/<int:id>', methods=['GET', 'POST'])
@login_required(role='Agent')
def update_priority(id):
	priority_id = Priority.query.get_or_404(id)
	form = PriorityForm()
	if form.validate_on_submit():
		priority_id.priority = form.priority.data
		db.session.commit()
		flash('Priority has been updated.', 'primary')
		return redirect(url_for('agent.priority'))
	return render_template('agent/priority.html', form=form)

@agent_blueprint.route('/priority/delete/<int:id>', methods=['GET', 'POST'])
@login_required(role='Agent')
def delete_priority(id):
	priority_id = Priority.query.get_or_404(id)
	if request.method == 'POST':
		db.session.delete(priority_id)
		db.session.commit()
		flash('Priority has been deleted.', 'primary')
		return redirect(url_for('agent.priority'))
	return redirect(url_for('agent.priority'))

@agent_blueprint.route('/statuses', methods=['GET'])
@login_required(role='Agent')
def status():
	statuses = Status.query.all()
	return render_template('agent/status.html', statuses=statuses)

@agent_blueprint.route('/my-profile', methods=['GET', 'POST'])
@login_required(role='Agent')
def my_profile():
	user = User.query.filter(User.id==current_user.id).first()
	form = ChangeProfileForm()
	if form.validate_on_submit():
		file = form.profile.data
		# Rename the uploaded file
		filename, ext = os.path.splitext(file.filename)
		filename = str(user.id)
		profile = secure_filename(filename + ext)
		# then save it to the designated folder
		file.save(os.path.join(current_app.config['PROFILE_DIR'], profile))

		user.image = profile
		db.session.commit()
		flash('Your profile has been changed.', 'primary')
		return redirect(url_for('agent.my_profile'))
	return render_template('agent/my_profile.html', form=form, user=user)

@agent_blueprint.route('/change-password', methods=['GET', 'POST'])
@login_required(role='Agent')
def change_password():
	user = User.query.filter(User.id==current_user.id).first()
	form = ChangePasswordForm()
	if form.validate_on_submit():
		hashed_password = generate_password_hash(form.password.data)
		user.password = hashed_password
		db.session.commit()
		flash('Your password has been changed.', 'primary')
		return redirect(url_for('agent.change_password'))
	return render_template('agent/change_password.html', form=form)

@agent_blueprint.route('/notifications', methods=['GET'])
@login_required(role='Agent')
def notifications():
	my_notifications = Notification.query.filter(Notification.receiver_id==current_user.id).order_by(desc(Notification.created_at)).all()
	return render_template('agent/notifications.html', my_notifications=my_notifications)

@agent_blueprint.route('/read-notification/<int:tid>/<int:nid>', methods=['GET'])
@login_required(role='Agent')
def read_notification(tid, nid):
	ticket_id = Ticket.query.get_or_404(tid)
	notification_id = Notification.query.get_or_404(nid)
	
	notification_id.seen = True
	db.session.commit()
	return redirect(url_for('agent.view_ticket', id=ticket_id.id))