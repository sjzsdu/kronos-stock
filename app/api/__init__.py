from flask import Blueprint

# Create API blueprint
api_bp = Blueprint('api', __name__)

# Import all API routes
from . import model
from . import stock
from . import prediction
from . import mock_routes
from . import market_news
from . import notifications
from . import alerts