import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app import create_app

# Create Flask application with new architecture
app = create_app(os.environ.get('FLASK_CONFIG', 'development'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print("🚀 Starting Kronos Stock Prediction System")
    print("📦 Using modern HTMX architecture")
    print(f"🌐 Server running on: http://localhost:{port}/")
    print(f"📊 Dashboard: http://localhost:{port}/dashboard")
    print(f"🔗 API docs: http://localhost:{port}/api/")
    print("=" * 50)
    
    app.run(debug=debug, host='0.0.0.0', port=port)