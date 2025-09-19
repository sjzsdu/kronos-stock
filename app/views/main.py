from flask import render_template, jsonify, redirect, url_for
from . import views_bp
from app.services import model_service
from datetime import datetime, timedelta
import random

@views_bp.route('/')
def index():
    """Index page"""
    return render_template('pages/index.html')

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
