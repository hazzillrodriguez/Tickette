from tests.BaseTestCase import BaseCase

class TestUserLogin(BaseCase):
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