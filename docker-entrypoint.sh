#!/bin/bash
# Database initialization script for Docker deployment

set -e

echo "🗄️  Initializing Kronos Stock Prediction Database..."

# Check if using cloud MySQL
if [ "$FLASK_CONFIG" = "production" ] && [[ "$DATABASE_URL" == *"mysql"* ]]; then
    echo "📡 Using cloud MySQL service..."
    
    # Optional: Add a simple connectivity test
    echo "🔍 Testing database connectivity..."
    python -c "
import os
import sys
from sqlalchemy import create_engine, text

try:
    engine = create_engine(os.environ['DATABASE_URL'])
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('✅ Database connection successful!')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    sys.exit(1)
" || {
        echo "❌ Failed to connect to cloud MySQL. Please check your DATABASE_URL."
        exit 1
    }
else
    echo "📁 Using SQLite database for development..."
fi

# Initialize database tables
echo "🏗️  Creating database tables..."
python init_db.py

echo "✅ Database initialization completed!"

# Start the application
echo "🚀 Starting Kronos Stock Prediction System..."
exec "$@"