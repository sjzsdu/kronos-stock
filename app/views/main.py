from flask import render_template, jsonify
from . import views_bp
from app.services import model_service
from datetime import datetime, timedelta
import random

@views_bp.route('/')
def index():
    """Modern main page with enhanced UI"""
    model_status = model_service.get_model_status()
    return render_template('pages/modern_index.html', model_status=model_status)

@views_bp.route('/modern')
def modern_index():
    """Modern index page"""
    model_status = model_service.get_model_status()
    return render_template('pages/modern_index.html', model_status=model_status)

@views_bp.route('/dashboard')
def dashboard():
    """Advanced dashboard page"""
    model_status = model_service.get_model_status()
    return render_template('pages/dashboard.html', model_status=model_status)

@views_bp.route('/stock-search')
def stock_search():
    """Stock search page"""
    model_status = model_service.get_model_status()
    return render_template('pages/stock_search.html', model_status=model_status)

@views_bp.route('/prediction')
def prediction():
    """AI prediction page"""
    model_status = model_service.get_model_status()
    return render_template('pages/prediction.html', model_status=model_status)

@views_bp.route('/history')
def history():
    """Prediction history page"""
    model_status = model_service.get_model_status()
    return render_template('pages/history.html', model_status=model_status)

@views_bp.route('/profile')
def profile():
    """User profile page"""
    model_status = model_service.get_model_status()
    return render_template('pages/profile.html', model_status=model_status)

@views_bp.route('/settings')
def settings():
    """System settings page"""
    model_status = model_service.get_model_status()
    return render_template('pages/settings.html', model_status=model_status)

@views_bp.route('/alerts')
def alerts():
    """System alerts page"""
    model_status = model_service.get_model_status()
    return render_template('pages/alerts.html', model_status=model_status)

@views_bp.route('/test')
def test():
    """System test page"""
    return render_template('pages/test.html')