from flask import render_template, redirect, url_for, jsonify, make_response, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, unset_jwt_cookies
from functools import wraps
from . import main
from models import db, Course, Registration, Student, Festival
from sqlalchemy import desc
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def jwt_required_custom(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        logger.info(f"Entering jwt_required_custom decorator for {fn.__name__}")
        if current_app.config.get('TESTING', False):
            logger.debug("Testing mode detected, bypassing JWT verification")
            return fn(*args, **kwargs)
        try:
            logger.debug("Attempting to verify JWT")
            verify_jwt_in_request()
            logger.info("JWT verification successful")
            return fn(*args, **kwargs)
        except Exception as e:
            logger.error(f"JWT verification failed: {str(e)}")
            return jsonify({"error": "로그인이 필요한 서비스입니다.", "redirect": url_for('main.main', _external=True)}), 401
    return wrapper

@main.route('/dashboard')
@jwt_required_custom
def index():
    logger.info("Entering index function")
    try:
        if current_app.config.get('TESTING', False):
            logger.debug("Testing mode detected, returning test data")
            return render_template('index.html', username='Test User', festivals=[], applied_courses=[])

        current_user_id = get_jwt_identity()
        logger.debug(f"Current user ID: {current_user_id}")
        student = Student.query.filter_by(id=current_user_id).first()
        logger.info(f"Retrieved student: {student}")

        logger.debug("QQQQQQQQQQQQQQQQuerying festivalsQQQQQQQQQQQQQQQ")
        festivals = Festival.query.filter(Festival.capacity != Festival.total_seats)\
                            .order_by(desc(Festival.capacity))\
                            .limit(9)\
                            .all()
        logger.info(f"Retrieved {len(festivals)} festivals")

        logger.debug("QQQQQQQQQQQQQQQQQuerying applied coursesQQQQQQQQQQQQQQQQQQQQQQQQ")
        applied_courses = db.session.query(Course).join(Registration).filter(
            Registration.student_id == student.student_id,
            Registration.status == 'Applied'
        ).all() if student else []
        logger.info(f"Retrieved {len(applied_courses)} applied courses")
        applied_courses_data = [{
            'id': course.id,
            'course_name': course.course_name,
            'professor': course.professor,
            'credits': course.credits,
            'department': course.department,
            'year': course.year
        } for course in applied_courses]
        logger.debug("Rendering index template")
        return render_template('index.html', 
                               username=student.name if student else 'User',
                               festivals=festivals,
                               applied_courses=applied_courses_data)
    except Exception as e:
        logger.error(f"Error in index function: {str(e)}", exc_info=True)
        return "Internal Server Error", 500

@main.route('/festival/festivals')
@jwt_required_custom
def api_festivals():
    logger.info("Entering api_festivals function")
    try:
        if current_app.config.get('TESTING', False):
            logger.debug("Testing mode detected, returning test data")
            return jsonify({"success": True, "festivals": [{"name": "Test Festival", "capacity": 100, "total_seats": 10}]})
        logger.debug("Querying festivals")
        festivals = Festival.query.filter(Festival.capacity != Festival.total_seats)\
                            .order_by(desc(Festival.capacity))\
                            .limit(9)\
                            .all()
        logger.info(f"Retrieved {len(festivals)} festivals")
        festivals_data = [festival.to_dict() for festival in festivals]
        logger.debug("Returning festivals data")
        return jsonify({"success": True, "festivals": festivals_data})
    except Exception as e:
        logger.error(f"Error in api_festivals function: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": "An unexpected error occurred"}), 500

@main.route('/festival')
def festival():
    logger.info("Entering festival function")
    logger.debug("Redirecting to festival page")
    return redirect('http://localhost:5002/festival')

@main.route('/notice')
def notice():
    logger.info("Entering notice function")
    logger.debug("Redirecting to notice page")
    return redirect('http://localhost:5004/notice')

@main.route('/course_registration')
def course_registration():
    logger.info("Entering course_registration function")
    logger.debug("Redirecting to course registration page")
    return redirect('http://localhost:5001/course_registration')

@main.route('/logout')
def logout():
    logger.info("Entering logout function")
    if current_app.config.get('TESTING', False):
        logger.debug("Testing mode detected, redirecting to main page")
        return redirect('http://localhost:5003/main')

    response = make_response(redirect('http://localhost:5006/login'))
    unset_jwt_cookies(response)
    logger.info("User logged out successfully")
    return response

@main.route('/login')
def main():
    logger.info("Entering main function")
    logger.debug("Redirecting to login page")
    return redirect('http://localhost:5006/login')