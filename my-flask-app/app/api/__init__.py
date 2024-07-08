from flask import Blueprint

api_blueprint = Blueprint('api', __name__)

from . import document_routes  # Ensure this import is at the end
