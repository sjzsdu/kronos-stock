from flask import Blueprint

# Create views blueprint
views_bp = Blueprint('views', __name__)

# Import views
from . import main
from . import components

# Import user system views
from . import auth_views
from . import user_views