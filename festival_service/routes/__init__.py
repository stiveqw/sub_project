from flask import Blueprint

festival = Blueprint('festival', __name__)

from . import views