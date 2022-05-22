from flask import Blueprint, current_app, render_template as _render, send_file, redirect, request, url_for, flash
from flask_login import current_user

from app.customer.forms import TicketForm, UpdateTicketForm, CommentForm, ChangeProfileForm, ChangePasswordForm
from app.models import User, Ticket, Comment, Notification

from app.utils.generate_digits import random_numbers
from app.utils.authorized_role import login_required
from app.exts import db

from werkzeug.utils import secure_filename

from sqlalchemy import desc

from werkzeug.security import generate_password_hash

import datetime
import uuid
import os

customer_blueprint = Blueprint('customer', __name__)
path = os.getcwd()

# Pass variable to all templates
def render_template(*args, **kwargs):
	notifications = Notification.query.filter(Notification.receiver_id==current_user.id).filter(Notification.seen==False).order_by(desc(Notification.created_at)).all()
	year = datetime.date.today().year
	return _render(*args, **kwargs, notifications=notifications, year=year)

@customer_blueprint.route('/dashboard')
@login_required(role='Customer')
def dashboard():
	id = current_user.id
	open = Ticket.query.filter_by(author_id=id).filter_by(status_id=1).all()
	solved = Ticket.query.filter_by(author_id=id).filter_by(status_id=2).all()
	pending = Ticket.query.filter_by(author_id=id).filter_by(status_id=3).all()
	closed = Ticket.query.filter_by(author_id=id).filter_by(status_id=4).all()
	
	return render_template('customer/dashboard.html', open=open, solved=solved, pending=pending, closed=closed)

@customer_blueprint.route('/my-tickets', methods=['GET'])
@login_required(role='Customer')
def my_tickets():
	tickets = Ticket.query.filter(Ticket.author_id==current_user.id).order_by(desc(Ticket.created_at)).all()
	form = TicketForm()
	return render_template('customer/my_tickets.html', form=form, tickets=tickets)

@customer_blueprint.route('/create-ticket', methods=['GET', 'POST'])
@login_required(role='Customer')
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
		return redirect(url_for('customer.my_tickets'))

@customer_blueprint.route('/view-ticket/<int:id>', methods=['GET', 'POST'])
@login_required(role='Customer')
def view_ticket(id):
	ticket = Ticket.query.filter(Ticket.author_id==current_user.id).filter_by(id=id).first()
	comments = Comment.query.filter(Comment.ticket_id==id).all()
	
	if not ticket:
		return redirect(url_for('customer.my_tickets'))
	
	form = UpdateTicketForm(category=ticket.category_id)
	comment_form = CommentForm()
	if form.validate_on_submit():
		if ticket.category_id != int(form.category.data) and ticket.owner_id is not None:
			Notification.send_notification(message='updated category on ticket', receiver_id=ticket.owner_id, sender_id=current_user.id, ticket_id=ticket.id, seen=False)
		ticket.category_id = form.category.data

		db.session.commit()
		flash('Ticket has been updated.', 'primary')
		return redirect(url_for('customer.view_ticket', id=id))
	return render_template('customer/view_ticket.html', form=form, comment_form=comment_form, ticket=ticket, comments=comments)

@customer_blueprint.route('/comment-ticket/<int:id>', methods=['GET', 'POST'])
@login_required(role='Customer')
def comment_ticket(id):
	ticket_id = Ticket.query.get_or_404(id)
	comment_form = CommentForm()
	if comment_form.validate_on_submit():
		author_id = ticket_id.author_id
		owner_id = ticket_id.owner_id
		comment = comment_form.comment.data

		message = 'commented on ticket'
		# Send notification to the owner, if the ticket is mine and is not assigned to me
		if author_id == current_user.id and owner_id != current_user.id and owner_id is not None:
			Notification.send_notification(message=message, receiver_id=owner_id, sender_id=current_user.id, ticket_id=ticket_id.id, seen=False)

		db.session.add(Comment(comment=comment, author_id=current_user.id, ticket_id=ticket_id.id))
		db.session.commit()
		flash('Your comment has been posted.', 'primary')
		return redirect(url_for('customer.view_ticket', id=id))
	return render_template('customer/view_ticket.html', comment_form=comment_form)

@customer_blueprint.route('/ticket/delete/<int:uid>/<int:tid>', methods=['GET', 'POST'])
@login_required(role='Customer')
def delete_ticket(uid, tid):
	ticket_id = Ticket.query.get_or_404(tid)
	if request.method == 'POST':
		if ticket_id.file_link:
			FOLDER_ID = os.path.join(path, 'app/static/uploads/attachments/' + str(uid))
			os.remove(os.path.join(FOLDER_ID, ticket_id.file_link))

		db.session.delete(ticket_id)
		db.session.commit()
		flash('Ticket has been deleted.', 'primary')
		return redirect(url_for('customer.my_tickets'))
	return redirect(url_for('customer.view_ticket', id=tid))

@customer_blueprint.route('/download/attachment/<int:id>/<filename>')
def download_attachment(id, filename):
	FOLDER_ID = os.path.join(path, 'app/static/uploads/attachments/' + str(id))
	location = os.path.join(FOLDER_ID, filename)
	return send_file(location, as_attachment=True)

@customer_blueprint.route('/my-profile', methods=['GET', 'POST'])
@login_required(role='Customer')
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
		return redirect(url_for('customer.my_profile'))
	return render_template('customer/my_profile.html', form=form, user=user)

@customer_blueprint.route('/change-password', methods=['GET', 'POST'])
@login_required(role='Customer')
def change_password():
	user = User.query.filter(User.id==current_user.id).first()
	form = ChangePasswordForm()
	if form.validate_on_submit():
		hashed_password = generate_password_hash(form.password.data)
		user.password = hashed_password
		db.session.commit()
		flash('Your password has been changed.', 'primary')
		return redirect(url_for('customer.change_password'))
	return render_template('customer/change_password.html', form=form)

@customer_blueprint.route('/notifications', methods=['GET'])
@login_required(role='Customer')
def notifications():
	my_notifications = Notification.query.filter(Notification.receiver_id==current_user.id).order_by(desc(Notification.created_at)).all()
	return render_template('customer/notifications.html', my_notifications=my_notifications)

@customer_blueprint.route('/read-notification/<int:tid>/<int:nid>', methods=['GET'])
@login_required(role='Customer')
def read_notification(tid, nid):
	ticket_id = Ticket.query.get_or_404(tid)
	notification_id = Notification.query.get_or_404(nid)
	
	notification_id.seen = True
	db.session.commit()
	return redirect(url_for('customer.view_ticket', id=ticket_id.id))