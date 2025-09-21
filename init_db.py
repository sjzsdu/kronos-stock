#!/usr/bin/env python3
"""Database initialization script for Kronos Stock Prediction System"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db

def init_db():
    """Initialize database"""
    # Get Flask environment
    config_name = os.environ.get('FLASK_CONFIG', 'development')
    
    print(f"Initializing database with config: {config_name}")
    
    # Create Flask app
    app = create_app(config_name)
    
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")
        
        # Print database URI (hide password for security)
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        if 'mysql' in db_uri and '@' in db_uri:
            # Hide password in MySQL URI
            uri_parts = db_uri.split('@')
            user_pass = uri_parts[0].split('//')[-1]
            if ':' in user_pass:
                user, _ = user_pass.split(':', 1)
                safe_uri = db_uri.replace(user_pass, f"{user}:***")
            else:
                safe_uri = db_uri
        else:
            safe_uri = db_uri
        
        print(f"Database URI: {safe_uri}")

if __name__ == '__main__':
    init_db()