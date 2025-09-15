from flask import render_template
from . import views_bp
from app.services import model_service

@views_bp.route('/')
def index():
    """Main dashboard page"""
    model_status = model_service.get_model_status()
    return render_template('pages/index.html', model_status=model_status)

@views_bp.route('/dashboard')
def dashboard():
    """Advanced dashboard page"""
    model_status = model_service.get_model_status()
    return render_template('pages/dashboard.html', model_status=model_status)