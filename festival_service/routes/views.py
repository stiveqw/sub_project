from flask import render_template, redirect, url_for, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, unset_jwt_cookies
from functools import wraps
import logging
import os
from . import festival
from models import Festival, db
from math import ceil

logger = logging.getLogger(__name__)

ITEMS_PER_PAGE = 3

def get_festival_images():
    image_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'images')
    return [f for f in os.listdir(image_dir) if f.startswith('festival_') and f.endswith('.jpg')]

@festival.route('/')
@jwt_required()
def home():
    try:
        verify_jwt_in_request()
        current_user = get_jwt_identity()
        logger.debug("JWT verified successfully")
        logger.info(f"User {current_user} accessed the festival page")
        
        page = request.args.get('page', 1, type=int)
        festivals = Festival.query.paginate(page=page, per_page=ITEMS_PER_PAGE, error_out=False)
        total_pages = ceil(festivals.total / ITEMS_PER_PAGE)
        
        festival_images = get_festival_images()
        
        return render_template('festival_main.html', 
                               festivals=festivals.items, 
                               page=page, 
                               total_pages=total_pages, 
                               get_festival_images=get_festival_images)
    except Exception as e:
        logger.error(f"Error in home route: {str(e)}")
        return jsonify({"error": "An error occurred while loading the festival page."}), 500

@festival.route('/redirect_to_main')
def redirect_to_main():
    return redirect('http://localhost:5003/')

@festival.route('/redirect_to_news')
def redirect_to_news():
    return redirect('http://localhost:5004/news')

@festival.route('/redirect_to_course')
def redirect_to_course():
    return redirect('http://localhost:5001/course_registration')

@festival.route('/logout')
@jwt_required()
def logout():
    response = make_response(redirect('http://localhost:5006/login'))
    unset_jwt_cookies(response)
    return response

@festival.route('/apply/<int:festival_id>')
@jwt_required()
def apply(festival_id):
    festival = Festival.query.get_or_404(festival_id)
    return render_template('festival_apply.html', festival=festival)

@festival.route('/login')
def login():
    return redirect('http://localhost:5006/login')

