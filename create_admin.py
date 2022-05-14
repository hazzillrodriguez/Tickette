from app import create_app
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash

from app.models import User
from app.exts import db

app = create_app()

name = 'Administrator'
email = 'admin@tickette.com'
password = 'admindemo'
role = 'Administrator'
image = 'default-profile.png'

hashed_password = generate_password_hash(password)

user = User(name=name, email=email, password=hashed_password, role=role, image=image)
def db_commit():
	try:
		db.session.commit()
		print('{} has been created'.format(email))
		return True
	except SQLAlchemyError:
		result = str(SQLAlchemyError)
		print(result)
		return False

with app.app_context():
	if db_commit():
		db.session.add(user)
		db.session.commit()