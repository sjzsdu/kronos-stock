from flask import Blueprint

# Create API blueprint
api_bp = Blueprint('api', __name__)

# Import all API routes
from . import model
from . import stock
from . import prediction