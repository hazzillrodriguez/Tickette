from flask import Blueprint, render_template, redirect, request, url_for, flash
from app.utils.authorized_role import login_required

customer_blueprint = Blueprint('customer', __name__)

@customer_blueprint.route('/dashboard')
@login_required(role='Customer')
def dashboard():
	return render_template('customer/dashboard.html')