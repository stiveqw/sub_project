from flask import render_template, redirect, url_for, request, jsonify, make_response, current_app
from flask_jwt_extended import jwt_required, unset_jwt_cookies, get_jwt_identity, verify_jwt_in_request, get_jwt, create_access_token
from functools import wraps
from . import course
from extensions import socketio
from models import db, Course, Registration, Student
from sqlalchemy.exc import SQLAlchemyError
import logging


logger = logging.getLogger(__name__)

# 메모리에 kept_courses 저장
kept_courses = {}

@course.route('/refresh-csrf', methods=['GET'])
@jwt_required()
def refresh_csrf():
    try:
        # 현재 사용자의 ID를 가져옵니다
        current_user_id = get_jwt_identity()
        
        # 새로운 액세스 토큰을 생성합니다
        new_token = create_access_token(identity=current_user_id)
        
        # 새로운 CSRF 토큰을 생성합니다 (Flask-JWT-Extended가 자동으로 처리)
        return jsonify({"csrf_token": new_token}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@course.route('/course_registration')
@jwt_required()
def course_service():
    logger.info(f"Received request for {request.path}")
    return render_template('course_service.html')

@course.route('/api/credits')
@jwt_required()
def get_credits():
    logger.info(f"Received request for {request.path}")
    credits = db.session.query(Course.credits).distinct().order_by(Course.credits).all()
    return jsonify({'credits': [credit[0] for credit in credits]})

@course.route('/api/departments')
@jwt_required()
def get_departments():
    logger.info(f"Received request for {request.path}")
    departments = db.session.query(Course.department).distinct().order_by(Course.department).all()
    return jsonify({'departments': [dept[0] for dept in departments]})

@course.route('/api/search_courses')
@jwt_required()
def search_courses():
    logger.info(f"Received request for {request.path}")
    try:
        credits = request.args.get('credits')
        department = request.args.get('department')
        course_name = request.args.get('course_name')

        query = Course.query

        if credits and credits != 'Select Credits':
            query = query.filter(Course.credits == int(credits))
        if department and department != 'Select Department':
            query = query.filter(Course.department == department)
        if course_name:
            query = query.filter(Course.course_name.ilike(f'%{course_name}%'))

        courses = query.all()
        courses_list = [{
            'id': course.id,
            'course_key': course.course_key,
            'course_name': course.course_name,
            'professor': course.professor,
            'max_students': course.max_students,
            'current_students': course.current_students,
            'credits': course.credits,
            'department': course.department,
            'year': course.year,
            'created_at': course.created_at.isoformat() if course.created_at else None
        } for course in courses]
        
        return jsonify({'success': True, 'courses': courses_list})
    except Exception as e:
        logger.error(f"Error in search_courses: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred while searching courses"}), 500

@course.route('/apply_course', methods=['POST'])
@jwt_required()
def apply_course():
    
    logger.info(f"Received request for {request.path}")
    try:
        data = request.get_json()
        course_key = data.get('course_key')
        
        user_id = get_jwt_identity()
        
        student = Student.query.filter_by(id=user_id).first()
        if not student:
            return jsonify({"success": False, "message": "Student not found"}), 404
        
        course = Course.query.filter_by(course_key=course_key).first()
        if not course:
            return jsonify({"success": False, "message": "Course not found"}), 404
        
        applied_count = Registration.query.filter_by(course_key=course.course_key, status='Applied').count()
        if applied_count >= course.max_students:
            logger.warning(f"Course {course_key} is full")
            return jsonify({"success": False, "message": "Course is full"}), 400
        
        registration = Registration.query.filter_by(course_key=course.course_key, student_id=student.student_id).first()
        
        if registration:
            if registration.status == 'Applied':
                logger.warning(f"Student {student.student_id} already applied for course {course_key}")
                return jsonify({"success": False, "message": "Already applied for this course"}), 400
            registration.status = 'Applied'
        else:
            registration = Registration(course_key=course.course_key, student_id=student.student_id, status='Applied')
            db.session.add(registration)
        
        db.session.commit()
        logger.info(f"Student {student.student_id} successfully applied for course {course_key}")
        return jsonify({"success": True, "message": "Successfully applied for the course"})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in apply_course: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred during course application"}), 500

@course.route('/api/cancel_course', methods=['POST'])
@jwt_required()
def cancel_course():
    logger.info(f"Received request for {request.path}")
    try:
        user_id = get_jwt_identity()
        logger.debug(f"Cancelling course for user: {user_id}")
        
        student = Student.query.filter_by(id=user_id).first()
        
        if not student:
            logger.error(f"Student not found for user ID: {user_id}")
            return jsonify({"success": False, "message": "Student not found"}), 404
        
        course_id = request.json.get('course_id')
        course = Course.query.get(course_id)
        
        if not course:
            logger.error(f"Course not found with ID: {course_id}")
            return jsonify({"success": False, "message": "Course not found"}), 404
        
        registration = Registration.query.filter_by(course_key=course.course_key, student_id=student.student_id).first()
        
        if not registration or registration.status != 'Applied':
            logger.warning(f"No active registration found for student {student.student_id} and course {course_id}")
            return jsonify({"success": False, "message": "No active registration found for this course"}), 400
        
        registration.status = 'Cancelled'
        db.session.commit()
        logger.info(f"Successfully cancelled course {course_id} for student {student.student_id}")
        return jsonify({"success": True, "message": "Successfully cancelled the course registration"})
    except Exception as e:
        logger.error(f"Error in cancel_course: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred while cancelling the course"}), 500

@course.route('/api/get_applied_courses', methods=['GET'])
@jwt_required()
def get_applied_courses():
    logger.info(f"Received request for {request.path}")
    try:
        user_id = get_jwt_identity()
        
        student = Student.query.filter_by(id=user_id).first()
        if not student:
            return jsonify({"success": False, "message": "Student not found"}), 404

        applied_courses = db.session.query(Course).join(Registration).filter(
            Registration.student_id == student.student_id,
            Registration.status == 'Applied'
        ).all()

        courses_data = [{
            'id': course.id,
            'course_name': course.course_name,
            'professor': course.professor,
            'credits': course.credits,
            'department': course.department,
            'year': course.year
        } for course in applied_courses]

        return jsonify({"success": True, "courses": courses_data}), 200

    except SQLAlchemyError as e:
        return jsonify({"success": False, "message": "Database error occurred"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@course.route('/redirect_to_main')
def redirect_to_main():
    logger.info(f"Received request for {request.path}")
    return redirect('http://localhost:5003/')

@course.route('/redirect_to_festival')
def redirect_to_festival():
    logger.info(f"Received request for {request.path}")
    return redirect('http://localhost:5002/')

@course.route('/redirect_to_news')
def redirect_to_news():
    logger.info(f"Received request for {request.path}")
    return redirect('http://localhost:5004/news')

@course.route('/logout')
@jwt_required()
def logout():
    logger.info(f"Received request for {request.path}")
    response = make_response(redirect('http://localhost:5006/login'))
    unset_jwt_cookies(response)
    return response

@course.route('/login')
def login():
    logger.info(f"Received request for {request.path}")
    return redirect('http://localhost:5006/login')

