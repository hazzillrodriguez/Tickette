from flask import Blueprint, render_template, redirect, request, url_for, flash
from app.utils.authorized_role import login_required

agent_blueprint = Blueprint('agent', __name__)

@agent_blueprint.route('/dashboard')
@login_required(role='Agent')
def dashboard():
	return render_template('agent/dashboard.html')