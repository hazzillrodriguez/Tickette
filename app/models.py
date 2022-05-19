from flask import current_app
from flask_login import UserMixin

from app.exts import db, login_manager
from sqlalchemy.sql import func
from sqlalchemy import event

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

# Database models
class User(db.Model, UserMixin):
	__tablename__ = 'users'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(255), nullable=False)
	email = db.Column(db.String(255), unique=True, nullable=False)
	password = db.Column(db.String(255), nullable=False)
	role = db.Column(db.String(255), nullable=False)
	image = db.Column(db.String(255), nullable=False)
	
	created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
	updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

	# Relationship
	author_tickets = db.relationship('Ticket', foreign_keys='Ticket.author_id',
		backref='author', cascade='all, delete-orphan', lazy=True)
	owner_tickets = db.relationship('Ticket', foreign_keys='Ticket.owner_id',
		backref='owner', passive_deletes=True, lazy=True)
	
	comments = db.relationship('Comment', backref='user', cascade='all, delete-orphan', lazy=True)
	
	receivers = db.relationship('Notification', foreign_keys='Notification.receiver_id',
		backref='receiver', cascade='all, delete-orphan', lazy=True)
	senders = db.relationship('Notification', foreign_keys='Notification.sender_id',
		backref='sender', cascade='all, delete-orphan', lazy=True)

	def get_reset_token(self, expires_sec=1800):
		serializer = Serializer(current_app.config['SECRET_KEY'], expires_sec)
		return serializer.dumps({'user_id': self.id}).decode('utf-8')

	@staticmethod
	def verify_reset_token(token):
		serializer = Serializer(current_app.config['SECRET_KEY'])
		try:
			user_id = serializer.loads(token)['user_id']
		except:
			return None
		return User.query.get(user_id)

	def __init__(self, name, email, password, role, image):
		self.name = name
		self.email = email
		self.password = password
		self.role = role
		self.image = image

@event.listens_for(User.__table__, 'after_create')
def create_users(*args, **kwargs):
	profile = 'default-profile.png'
	db.session.add(User(name='Ryan Reynolds', email='admin@tickette.com', password=generate_password_hash('admindemo'), role='Administrator', image=profile))
	db.session.add(User(name='Robert Downey', email='agent@tickette.com', password=generate_password_hash('agentdemo'), role='Agent', image=profile))
	db.session.add(User(name='Jeremy Renner', email='customer@tickette.com', password=generate_password_hash('customerdemo'), role='Customer', image=profile))
	db.session.commit()

class Ticket(db.Model):
	__tablename__ = 'tickets'

	id = db.Column(db.Integer, primary_key=True)
	number = db.Column(db.String(255), unique=True, nullable=False)
	subject = db.Column(db.String(255), nullable=False)
	body = db.Column(db.Text, nullable=False)
	
	author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
	owner_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
	
	category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
	priority_id = db.Column(db.Integer, db.ForeignKey('priorities.id', ondelete='SET NULL'), nullable=True)
	status_id = db.Column(db.Integer, db.ForeignKey('statuses.id', ondelete='SET NULL'), nullable=True)
	
	orig_file = db.Column(db.String(255), nullable=True)
	file_link = db.Column(db.String(255), nullable=True)

	created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
	updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

	# Relationship
	comments = db.relationship('Comment', backref='ticket_comment', cascade='all, delete-orphan', lazy=True)
	notifications = db.relationship('Notification', backref='ticket_notification', cascade='all, delete-orphan', lazy=True)

	def __init__(self, number, subject, body, author_id, owner_id, category_id, priority_id, status_id, orig_file, file_link):
		self.number = number
		self.subject = subject
		self.body = body
		
		self.author_id = author_id
		self.owner_id = owner_id
		
		self.category_id = category_id
		self.priority_id = priority_id
		self.status_id = status_id
		
		self.orig_file = orig_file
		self.file_link = file_link

class Category(db.Model):
	__tablename__ = 'categories'

	id = db.Column(db.Integer, primary_key=True)
	category = db.Column(db.String(255), nullable=False)
	
	created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
	updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

	# Relationship
	tickets = db.relationship('Ticket', backref='category', passive_deletes=True, lazy=True)

	def __init__(self, category):
		self.category = category

@event.listens_for(Category.__table__, 'after_create')
def create_categories(*args, **kwargs):
	db.session.add(Category(category='Help and support'))
	db.session.commit()

class Priority(db.Model):
	__tablename__ = 'priorities'

	id = db.Column(db.Integer, primary_key=True)
	priority = db.Column(db.String(255), nullable=False)
	
	created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
	updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

	# Relationship
	tickets = db.relationship('Ticket', backref='priority', passive_deletes=True, lazy=True)

	def __init__(self, priority):
		self.priority = priority

@event.listens_for(Priority.__table__, 'after_create')
def create_priorities(*args, **kwargs):
	db.session.add(Priority(priority='Low'))
	db.session.add(Priority(priority='Medium'))
	db.session.add(Priority(priority='High'))
	db.session.add(Priority(priority='Urgent'))
	db.session.commit()

class Status(db.Model):
	__tablename__ = 'statuses'

	id = db.Column(db.Integer, primary_key=True)
	status = db.Column(db.String(255), nullable=False)
	
	created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

	# Relationship
	tickets = db.relationship('Ticket', backref='status', passive_deletes=True, lazy=True)

	def __init__(self, status):
		self.status = status

@event.listens_for(Status.__table__, 'after_create')
def create_statuses(*args, **kwargs):
	db.session.add(Status(status='Open'))
	db.session.add(Status(status='Solved'))
	db.session.add(Status(status='Pending'))
	db.session.add(Status(status='Closed'))
	db.session.commit()

class Comment(db.Model):
	__tablename__ = 'comments'

	id = db.Column(db.Integer, primary_key=True)
	comment = db.Column(db.Text, nullable=False)
	
	author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
	ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
	
	created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

	def __init__(self, comment, author_id, ticket_id):
		self.comment = comment
		self.author_id = author_id
		self.ticket_id = ticket_id

class Notification(db.Model):
	__tablename__ = 'notifications'

	id = db.Column(db.Integer, primary_key=True)
	message = db.Column(db.String(255), nullable=False)

	receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
	sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

	ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
	seen = db.Column(db.Boolean, default=False, nullable=False)

	created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

	def __init__(self, message, receiver_id, sender_id, ticket_id, seen):
		self.message = message
		self.receiver_id = receiver_id
		self.sender_id = sender_id
		self.ticket_id = ticket_id
		self.seen = seen
	
	@classmethod
	def send_notification(cls, **kw):
		obj = cls(**kw)
		db.session.add(obj)
		db.session.commit()