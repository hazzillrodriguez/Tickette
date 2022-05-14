from flask import Flask, redirect, url_for
from flask_migrate import Migrate

from app.exts import db, login_manager, mail, csrf
from app.models import User, Ticket, Category, Priority, Status, Comment, Notification

def create_app():
	app = Flask(__name__)
	# Configuration
	if app.config['ENV'] == 'development':
		app.config.from_object('config.DevelopmentConfig')
	else:
		app.config.from_object('config.ProductionConfig')

	db.init_app(app)
	login_manager.init_app(app)

	migrate = Migrate(app, db)
	mail.init_app(app)
	csrf.init_app(app)

	from app.auth.views import auth_blueprint
	from app.admin.views import admin_blueprint
	from app.agent.views import agent_blueprint
	from app.customer.views import customer_blueprint

	app.register_blueprint(auth_blueprint)
	app.register_blueprint(admin_blueprint, url_prefix='/admin')
	app.register_blueprint(agent_blueprint, url_prefix='/agent')
	app.register_blueprint(customer_blueprint, url_prefix='/customer')

	@app.shell_context_processor
	def make_shell_context():
		return {
			'db': db,
			'User': User,
			'Ticket': Ticket,
			'Category': Category,
			'Priority': Priority,
			'Status': Status,
			'Comment': Comment,
			'Notification': Notification
		}
	
	return app