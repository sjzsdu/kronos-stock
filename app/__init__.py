from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_login import LoginManager
import config as config_module
from datetime import datetime

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_module.config[config_name])
    config_module.config[config_name].init_app(app)
    
    # Initialize database
    from app.models import db
    db.init_app(app)
    
    # Initialize Flask-Migrate
    migrate = Migrate(app, db)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth_views.login_page'
    login_manager.login_message = '请先登录以访问该页面'
    login_manager.login_message_category = 'info'
    login_manager.remember_cookie_duration = app.config['PERMANENT_SESSION_LIFETIME']
    login_manager.session_protection = 'strong'
    
    @login_manager.user_loader
    def load_user(user_id):
        """加载用户回调函数"""
        from app.models.user import User
        return User.query.get(int(user_id))
    
    # Initialize extensions
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Initialize user cache service
    from app.services.user_cache_service import init_user_cache_service
    init_user_cache_service(app)
    
    # Initialize optimized auth middleware
    from app.middleware.optimized_auth_middleware import init_optimized_auth_middleware
    init_optimized_auth_middleware(app)
    
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
    
    # Register template context processors
    @app.context_processor
    def menu_processor():
        """Provide menu data to all templates"""
        from flask import request
        from app.config.menu import (
            PRIMARY_MENU, 
            get_theme_for_endpoint, 
            get_sidebar_menu_for_theme,
            should_use_sidebar
        )
        
        current_endpoint = request.endpoint if request.endpoint else None
        current_theme = get_theme_for_endpoint(current_endpoint)
        sidebar_menu = get_sidebar_menu_for_theme(current_theme) if current_theme else []
        
        return {
            'primary_menu': PRIMARY_MENU,
            'current_theme': current_theme,
            'sidebar_menu': sidebar_menu,
            'should_use_sidebar': should_use_sidebar(current_endpoint),
            'current_endpoint': current_endpoint,
            'get_sidebar_menu_for_theme': get_sidebar_menu_for_theme,
            'get_theme_for_endpoint': get_theme_for_endpoint
        }
    
    # Register blueprints
    from app.api import api_bp
    from app.views import views_bp
    from app.api.prediction import prediction_api
    from app.api.market import market_api
    
    # Register user system blueprints
    from app.api.auth import auth_bp as api_auth_bp
    from app.api.user import user_bp as api_user_bp
    from app.views.auth import auth_bp
    from app.views.user_views import user_views
    from app.views.legal import legal_bp
    
    # Register UI enhancement blueprints
    from app.api.ui_components import ui_components_bp
    from app.api.user_preferences import user_preferences_bp
    from app.api.performance import performance_bp
    from app.api.usage_tracking import usage_tracking_bp
    from app.views.ui_components import ui_components_views_bp
    from app.views.ui_forms import ui_forms_views_bp
    from app.views.ui_modals import ui_modals_views_bp
    from app.views.ui_notifications import ui_notifications_views_bp
    
    app.register_blueprint(views_bp)
    app.register_blueprint(prediction_api, url_prefix='/api')
    app.register_blueprint(market_api, url_prefix='/api')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Register user system blueprints
    app.register_blueprint(api_auth_bp)
    app.register_blueprint(api_user_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_views)
    app.register_blueprint(legal_bp)
    
    # Register UI enhancement API blueprints
    app.register_blueprint(ui_components_bp)
    app.register_blueprint(user_preferences_bp)
    app.register_blueprint(performance_bp)
    app.register_blueprint(usage_tracking_bp)
    
    # Register UI enhancement view blueprints
    app.register_blueprint(ui_components_views_bp)
    app.register_blueprint(ui_forms_views_bp)
    app.register_blueprint(ui_modals_views_bp)
    app.register_blueprint(ui_notifications_views_bp)
    
    # Setup API error handlers
    # Error handlers are now defined directly in the blueprint
    
    # Initialize model service with default model
    with app.app_context():
        from app.services import model_service
        try:
            # Try to load default model (kronos-mini for faster startup)
            success, message = model_service.load_model('kronos-mini')
            if success:
                app.logger.info(f"✅ Default model loaded: {message}")
            else:
                app.logger.warning(f"⚠️  Failed to load default model: {message}")
        except Exception as e:
            app.logger.error(f"❌ Model initialization error: {e}")
        
        # 为SQLite启用外键约束
        if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
            from sqlalchemy import event
            
            @event.listens_for(db.engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
    
    return app