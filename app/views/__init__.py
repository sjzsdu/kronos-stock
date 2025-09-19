from flask import Blueprint

# Create views blueprint
views_bp = Blueprint('views', __name__)

# Import views
from . import main
from . import components