from tests.BaseTestCase import BaseCase

class TestUserSignup(BaseCase):
	def test_signup_successful(self):
		response = self.client.post('/signup',
			data=dict(
				name='Test',
				email='test@tickette.com',
				password='testdemo',
				agree=True
			), follow_redirects=True)
		self.assertEqual(response.status_code, 200)

	def test_signup_email_already_exist(self):
		response = self.client.post('/signup',
			data=dict(
				name='Test',
				email='admin@tickette.com',
				password='testdemo',
				agree=True
			), follow_redirects=True)
		self.assertIn(b'This e-mail address is already taken', response.data)

	def test_signup_password_length(self):
		response = self.client.post('/signup',
			data=dict(
				name='Test',
				email='user@tickette.com',
				password='test',
				agree=True
			), follow_redirects=True)
		self.assertIn(b'Field must be between 6 and 32 characters long.', response.data)