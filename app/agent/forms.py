from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed

from wtforms import StringField, PasswordField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo

from app.models import User, Category, Priority, Status

from sqlalchemy import or_

allowed_exts = ['pdf', 'docx', 'png', 'jpg', 'jpeg', 'gif']

class TicketForm(FlaskForm):
	subject = StringField('Subject',
		validators=[DataRequired(), Length(min=4, max=128)])
	category = SelectField('Category',
		validators=[DataRequired()])
	body = TextAreaField('Message',
		validators=[DataRequired()])
	attachment = FileField('Attachment',
		validators=[FileAllowed(allowed_exts, 'This file extension is not allowed')])

	def __init__(self, *args, **kwargs):
		super(TicketForm, self).__init__(*args, **kwargs)
		self.category.choices = [('', '-- Please select category --')]+[(category.id, category.category) for category in Category.query.all()]

class UpdateTicketForm(FlaskForm):
	priority = SelectField('Priority',
		validators=[DataRequired()])
	status = SelectField('Status',
		validators=[DataRequired()])
	owner = SelectField('Assignee')

	def __init__(self, *args, **kwargs):
		super(UpdateTicketForm, self).__init__(*args, **kwargs)
		self.owner.choices = [('', '-- Choose an assignee --')]+[(owner.id, owner.name)
			for owner in User.query.filter(or_(User.role=='Administrator', User.role=='Agent')).all()]
		self.priority.choices = [('', '-- Please select priority --')]+[(priority.id, priority.priority)
			for priority in Priority.query.all()]
		self.status.choices = [('', '-- Please select status --')]+[(status.id, status.status)
			for status in Status.query.all()]

class CategoryForm(FlaskForm):
	category = StringField('Category',
		validators=[DataRequired(), Length(min=4, max=64)])

class PriorityForm(FlaskForm):
	priority = StringField('Priority',
		validators=[DataRequired(), Length(min=4, max=32)])

class CommentForm(FlaskForm):
	comment = TextAreaField('Comment',
		validators=[DataRequired()])

class ChangeProfileForm(FlaskForm):
	profile = FileField('Change Profile',
		validators=[FileRequired(), FileAllowed(['png', 'jpg', 'jpeg'], 'This file extension is not allowed')])

class ChangePasswordForm(FlaskForm):
	password = PasswordField('New Password',
		validators=[DataRequired(), Length(min=6, max=32)])
	confirm_password = PasswordField('Confirm Password',
		validators=[DataRequired(), EqualTo('password')])