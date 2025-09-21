import os
from typing import Dict, Any

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///kronos_stock.db'
    
    # Model configurations
    MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
    EMBEDDED_MODEL_DIR = os.path.join(os.path.dirname(__file__), 'model')
    
    # Available models configuration
    AVAILABLE_MODELS = {
        'kronos-mini': {
            'path': 'kronos-mini',
            'description': 'Lightweight model for fast inference',
            'size': 'Small (~100MB)',
            'performance': 'Fast'
        },
        'kronos-small': {
            'path': 'kronos-small', 
            'description': 'Balanced model for general use',
            'size': 'Medium (~500MB)',
            'performance': 'Balanced'
        },
        'kronos-base': {
            'path': 'kronos-base',
            'description': 'Full-featured model for best accuracy',
            'size': 'Large (~1GB)',
            'performance': 'Best'
        }
    }
    
    # Default prediction parameters
    DEFAULT_PREDICTION_PARAMS = {
        'lookback': 30,
        'pred_len': 5,
        'temperature': 0.7
    }
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # Production uses MySQL by default
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"mysql+pymysql://{os.environ.get('DB_USER', 'root')}:" \
        f"{os.environ.get('DB_PASSWORD', 'password')}@" \
        f"{os.environ.get('DB_HOST', 'localhost')}:" \
        f"{os.environ.get('DB_PORT', '3306')}/" \
        f"{os.environ.get('DB_NAME', 'kronos_stock')}"

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}