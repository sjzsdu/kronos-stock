from flask import Flask
from flask_cors import CORS
from config import config
from datetime import datetime

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Register custom template filters
    @app.template_filter('format_datetime')
    def format_datetime(value):
        """Format datetime string for display"""
        if isinstance(value, str):
            try:
                dt = datetime.strptime(value, '%Y-%m-%d %H:%M')
                return dt.strftime('%m-%d %H:%M')
            except:
                return value
        return value
    
    # Register blueprints
    from app.api import api_bp
    from app.views import views_bp
    
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(views_bp)
    
    return app