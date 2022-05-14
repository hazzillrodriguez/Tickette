from app import create_app
from app.models import Category, Priority, Status
from app.exts import db
from sqlalchemy.exc import SQLAlchemyError

app = create_app()

category = 'Help and Support'
priorities = ['Low', 'Medium', 'High', 'Urgent']
statuses = ['Open', 'Solved', 'Pending', 'Closed']

def db_commit():
	try:
		db.session.commit()
		print('category, priorities, and statuses has been created')
		return True
	except SQLAlchemyError:
		result = str(SQLAlchemyError)
		print(result)
		return False

with app.app_context():
	if db_commit():
		db.session.add(Category(category=category))
		
		for priority, status in zip(priorities, statuses):
			db.session.add(Priority(priority=priority))
			db.session.add(Status(status=status))
		
		db.session.commit()