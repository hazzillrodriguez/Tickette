from tests.BaseTestCase import BaseCase
from io import BytesIO

class TestAdminFunc(BaseCase):
	def test_admin_create_ticket(self):
		self.client.post('/login',
			data=dict(email='admin@tickette.com', password='admindemo'),
			follow_redirects=True)

		response = self.client.post('/admin/create-ticket',
			data=dict(
				subject='Test title',
				category=1,
				body='Test body',
				attachment=None
			), follow_redirects=True)
		self.assertIn(b'Ticket has been created.', response.data)

	def test_admin_update_ticket(self):
		self.client.post('/login',
			data=dict(email='admin@tickette.com', password='admindemo'),
			follow_redirects=True)

		self.client.post('/admin/create-ticket',
			data=dict(
				subject='Test title 2',
				category=1,
				body='Test body 2',
				attachment=None
			), follow_redirects=True)

		response = self.client.post('/admin/view-ticket/1',
			data=dict(
				priority=1,
				status=1,
				owner=1
			), follow_redirects=True)
		self.assertIn(b'Ticket has been updated.', response.data)

	def test_admin_delete_ticket(self):
		self.client.post('/login',
			data=dict(email='admin@tickette.com', password='admindemo'),
			follow_redirects=True)

		self.client.post('/admin/create-ticket',
			data=dict(
				subject='Test title 2',
				category=1,
				body='Test body 2',
				attachment=None
			), follow_redirects=True)

		response = self.client.post('/admin/ticket/delete/1/1',
			follow_redirects=True)
		self.assertIn(b'Ticket has been deleted.', response.data)

	def test_admin_post_comment(self):
		self.client.post('/login',
			data=dict(email='admin@tickette.com', password='admindemo'),
			follow_redirects=True)

		self.client.post('/admin/create-ticket',
			data=dict(
				subject='Test title',
				category=1,
				body='Test body',
				attachment=None
			), follow_redirects=True)

		response = self.client.post('/admin/comment-ticket/1',
			data=dict(comment='Hello?'), follow_redirects=True)
		self.assertIn(b'Your comment has been posted.', response.data)

	def test_admin_create_category(self):
		self.client.post('/login',
			data=dict(email='admin@tickette.com', password='admindemo'),
			follow_redirects=True)

		response = self.client.post('/admin/categories',
			data=dict(category='Technical issues'),
			follow_redirects=True)
		self.assertIn(b'Category has been created.', response.data)

	def test_admin_update_category(self):
		self.client.post('/login',
			data=dict(email='admin@tickette.com', password='admindemo'),
			follow_redirects=True)

		response = self.client.post('/admin/category/update/1',
			data=dict(category='Payment/Billing issues'),
			follow_redirects=True)
		self.assertIn(b'Category has been updated.', response.data)

	def test_admin_delete_category(self):
		self.client.post('/login',
			data=dict(email='admin@tickette.com', password='admindemo'),
			follow_redirects=True)

		response = self.client.post('/admin/category/delete/1',
			follow_redirects=True)
		self.assertIn(b'Category has been deleted.', response.data)

	def test_admin_create_priority(self):
		self.client.post('/login',
			data=dict(email='admin@tickette.com', password='admindemo'),
			follow_redirects=True)

		response = self.client.post('/admin/priorities',
			data=dict(priority='Important'),
			follow_redirects=True)
		self.assertIn(b'Priority has been created.', response.data)

	def test_admin_update_priority(self):
		self.client.post('/login',
			data=dict(email='admin@tickette.com', password='admindemo'),
			follow_redirects=True)

		response = self.client.post('/admin/priority/update/1',
			data=dict(priority='Very Important'),
			follow_redirects=True)
		self.assertIn(b'Priority has been updated.', response.data)

	def test_admin_delete_priority(self):
		self.client.post('/login',
			data=dict(email='admin@tickette.com', password='admindemo'),
			follow_redirects=True)

		response = self.client.post('/admin/priority/delete/1',
			follow_redirects=True)
		self.assertIn(b'Priority has been deleted.', response.data)

	def test_admin_create_account(self):
		self.client.post('/login',
			data=dict(email='admin@tickette.com', password='admindemo'),
			follow_redirects=True)

		response = self.client.post('/admin/create-account',
			data=dict(
				name='John',
				email='john@demo.com',
				password='johndemo',
				role='Customer'), follow_redirects=True)
		self.assertIn(b'john@demo.com has been created.', response.data)

	def test_admin_update_user_role(self):
		self.client.post('/login',
			data=dict(email='admin@tickette.com', password='admindemo'),
			follow_redirects=True)

		response = self.client.post('/admin/user/update/1',
			data=dict(role='Agent'), follow_redirects=True)
		self.assertIn(b'User role has been updated.', response.data)

	def test_admin_delete_user(self):
		self.client.post('/login',
			data=dict(email='admin@tickette.com', password='admindemo'),
			follow_redirects=True)

		self.client.post('/admin/create-account',
			data=dict(
				name='Johnson',
				email='johnson@demo.com',
				password='johndemo',
				role='Customer'), follow_redirects=True)

		response = self.client.post('/admin/user/delete/4',
			follow_redirects=True)
		self.assertIn(b'User has been deleted.', response.data)

	def test_admin_change_profile(self):
		self.client.post('/login',
			data=dict(email='admin@tickette.com', password='admindemo'),
			follow_redirects=True)

		data = dict(profile=(BytesIO(b'File content'), 'test.png'))
		response = self.client.post('/admin/my-profile',
			data=data,
			content_type='multipart/form-data',
			follow_redirects=True)
		self.assertIn(b'Your profile has been changed.', response.data)

	def test_admin_change_password_successful(self):
		self.client.post('/login',
			data=dict(email='admin@tickette.com', password='admindemo'),
			follow_redirects=True)

		response = self.client.post('/admin/change-password',
			data=dict(
				password='testdemo',
				confirm_password='testdemo'), follow_redirects=True)
		self.assertIn(b'Your password has been changed.', response.data)

	def test_admin_change_password_invalid(self):
		self.client.post('/login',
			data=dict(email='admin@tickette.com', password='admindemo'),
			follow_redirects=True)

		response = self.client.post('/admin/change-password',
			data=dict(
				password='testdemo',
				confirm_password='testuser'), follow_redirects=True)
		self.assertIn(b'Field must be equal to password.', response.data)

	def test_admin_logout(self):
		self.client.post('/login',
			data=dict(email='admin@tickette.com', password='admindemo'),
			follow_redirects=True)

		response = self.client.get('/logout', follow_redirects=True)
		self.assertIn(b'Login', response.data)