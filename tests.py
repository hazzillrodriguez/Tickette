from app import create_app
from app.exts import db
import unittest

class BaseCase(unittest.TestCase):
	def setUp(self):
		self.app = create_app()
		self.app.config.from_object('config.TestConfig')
		self.client = self.app.test_client(self)

		with self.app.app_context():
			db.init_app(self.app)
			db.create_all()

	def tearDown(self):
		with self.app.app_context():
			db.session.remove()
			db.drop_all()

	def test_login_successful(self):
		response = self.client.post('/login',
			data=dict(email='admin@tickette.com', password='admindemo'),
			follow_redirects=True)
		self.assertIn(b'Dashboard', response.data)

	def test_login_invalid(self):
		response = self.client.post('/login',
			data=dict(email='admin@tickette.com', password='admintest'),
			follow_redirects=True)
		self.assertIn(b'Your email or password is incorrect, please try again!', response.data)

	def test_signup_successful(self):
		response = self.client.post('/signup',
			data=dict(
				name='Test',
				email='test@tickette.com',
				password='testdemo',
				role='Customer',
				image='default-profile.png'
			), follow_redirects=True)
		self.assertEqual(response.status_code, 200)

	def test_signup_email_already_exist(self):
		response = self.client.post('/signup',
			data=dict(
				name='Test',
				email='admin@tickette.com',
				password='testdemo',
				role='Customer',
				image='default-profile.png'
			), follow_redirects=True)
		self.assertIn(b'This e-mail address is already taken', response.data)

	def test_signup_password_length(self):
		response = self.client.post('/signup',
			data=dict(
				name='Test',
				email='user@tickette.com',
				password='test',
				role='Customer',
				image='default-profile.png'
			), follow_redirects=True)
		self.assertIn(b'Field must be between 6 and 32 characters long.', response.data)

	def test_admin_create_category(self):
		response = self.client.post('/login',
			data=dict(email='admin@tickette.com', password='admindemo'),
			follow_redirects=True)

		response = self.client.post('/admin/categories',
			data=dict(category='Technical issues'),
			follow_redirects=True)
		self.assertIn(b'Category has been created.', response.data)

	def test_admin_update_category(self):
		response = self.client.post('/login',
			data=dict(email='admin@tickette.com', password='admindemo'),
			follow_redirects=True)

		response = self.client.post('/admin/category/update/1',
			data=dict(category='Payment/Billing issues'),
			follow_redirects=True)
		self.assertIn(b'Category has been updated.', response.data)

	def test_admin_delete_category(self):
		response = self.client.post('/login',
			data=dict(email='admin@tickette.com', password='admindemo'),
			follow_redirects=True)

		response = self.client.post('/admin/category/delete/1',
			follow_redirects=True)
		self.assertIn(b'Category has been deleted.', response.data)

	def test_admin_create_priority(self):
		response = self.client.post('/login',
			data=dict(email='admin@tickette.com', password='admindemo'),
			follow_redirects=True)

		response = self.client.post('/admin/priorities',
			data=dict(priority='Important'),
			follow_redirects=True)
		self.assertIn(b'Priority has been created.', response.data)

	def test_admin_update_priority(self):
		response = self.client.post('/login',
			data=dict(email='admin@tickette.com', password='admindemo'),
			follow_redirects=True)

		response = self.client.post('/admin/priority/update/1',
			data=dict(priority='Very Important'),
			follow_redirects=True)
		self.assertIn(b'Priority has been updated.', response.data)

	def test_admin_delete_priority(self):
		response = self.client.post('/login',
			data=dict(email='admin@tickette.com', password='admindemo'),
			follow_redirects=True)

		response = self.client.post('/admin/priority/delete/1',
			follow_redirects=True)
		self.assertIn(b'Priority has been deleted.', response.data)

	def test_admin_create_account(self):
		response = self.client.post('/login',
			data=dict(email='admin@tickette.com', password='admindemo'),
			follow_redirects=True)

		response = self.client.post('/admin/create-account',
			data=dict(
				name='John',
				email='john@demo.com',
				password='johndemo',
				role='Customer',
				image='default-profile.png'), follow_redirects=True)
		self.assertIn(b'john@demo.com has been created.', response.data)

	def test_admin_update_user_role(self):
		response = self.client.post('/login',
			data=dict(email='admin@tickette.com', password='admindemo'),
			follow_redirects=True)

		response = self.client.post('/admin/user/update/1',
			data=dict(role='Agent'), follow_redirects=True)
		self.assertIn(b'User role has been updated.', response.data)

	def test_admin_delete_user(self):
		response = self.client.post('/login',
			data=dict(email='admin@tickette.com', password='admindemo'),
			follow_redirects=True)

		response = self.client.post('/admin/user/delete/2',
			follow_redirects=True)
		self.assertIn(b'User has been deleted.', response.data)

	def test_admin_logout(self):
		response = self.client.post('/login',
			data=dict(email='admin@tickette.com', password='admindemo'),
			follow_redirects=True)

		response = self.client.get('/logout', follow_redirects=True)
		self.assertIn(b'Login', response.data)

if __name__ == '__main__':
	unittest.main()