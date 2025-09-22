from flask import Blueprint

# Create API blueprint
api_bp = Blueprint('api', __name__)

# Import existing API routes
from . import model
from . import stock