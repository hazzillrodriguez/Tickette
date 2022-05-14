from flask import redirect, request, url_for
from flask_login import current_user
from functools import wraps

def login_required(role='any'):
	def wrapper(fn):
		@wraps(fn)
		def decorated_view(*args, **kwargs):
			if not current_user.is_authenticated:
				# If user is not authenticated
				# redirect to login and set the url endpoint in the 'next' parameter
				return redirect(url_for('auth.login', next=request.endpoint))
			if current_user.role != role and role != 'any':
				return redirect(url_for('auth.login', next=request.endpoint))
			return fn(*args, **kwargs)
		return decorated_view
	return wrapper