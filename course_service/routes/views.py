from flask import render_template, redirect, url_for, request, jsonify, make_response, current_app
from flask_jwt_extended import jwt_required, unset_jwt_cookies, get_jwt_identity, verify_jwt_in_request
from werkzeug.exceptions import Unauthorized, UnprocessableEntity
from . import course
from functools import wraps
from models import db, Course, Registration, Student
from sqlalchemy.exc import SQLAlchemyError
from flask import Flask
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TEST_USER_ID = 99

def jwt_req_custom(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not app.config['TESTING']:
            logger.info(f"Attempting JWT verification for function: {fn.__name__}")
            try:
                verify_jwt_in_request()
                logger.info("JWT verification successful")
            except Exception as e:
                logger.error(f"JWT verification failed: {str(e)}")
                raise
        else:
            logger.info(f"JWT verification optional (Testing mode) for function: {fn.__name__}")
            verify_jwt_in_request(optional=True)
        return fn(*args, **kwargs)
    return wrapper

def get_current_user_id():
    if app.config['TESTING']:
        logger.info(f"Using test user ID: {TEST_USER_ID}")
        return TEST_USER_ID
    user_id = get_jwt_identity()
    logger.info(f"Retrieved user ID from JWT: {user_id}")
    return user_id

@course.route('/course_registration')
def course_registration():
    logger.info("수강 신청 엔드포인트 접근")
    try:
        logger.info("수강 신청을 위한 JWT 검증 시도")
        verify_jwt_in_request()
        logger.info("JWT 검증 성공, 수강 신청 페이지 렌더링")
        return render_template('course_service.html')
    except Exception as e:
        logger.error(f"수강 신청을 위한 JWT 검증 실패: {str(e)}")
        return render_template('auth_required.html'), 401

@course.route('/course_registration/get_courses', methods=['GET'])
@jwt_req_custom
def get_courses():
    logger.info('Fetching courses')
    try:
        # Return empty list for courses
        courses_data = []

        # 현재 사용자의 ID 가져오기
        current_user_id = get_current_user_id()
        
        # 현재 사용자의 신청한 과목 정보 가져오기
        student = Student.query.filter_by(id=current_user_id).first()
        if student:
            applied_courses = db.session.query(Course).join(Registration).filter(
                Registration.student_id == student.student_id,
                Registration.status == 'Applied'
            ).all()
            
            applied_courses_data = [{
                'id': course.id,
                'course_key': course.course_key,
                'course_name': course.course_name,
                'professor': course.professor,
                'credits': course.credits,
                'department': course.department,
                'year': course.year
            } for course in applied_courses]
        else:
            applied_courses_data = []
        logger.info(f'Fetched {len(applied_courses_data)} applied courses for user {current_user_id}')
        return jsonify({
            "success": True, 
            "courses": courses_data,
            "appliedCourses": applied_courses_data
        }), 200
    except Exception as e:
        logger.error(f'Error occurred while fetching courses: {str(e)}')
        return jsonify({"success": False, "message": "An error occurred while fetching courses"}), 500

@course.route('/course_registration/dropdown_options', methods=['GET'])
@jwt_req_custom
def get_dropdown_options():
    logger.info('Fetching dropdown options')
    try:
        credits = db.session.query(Course.credits).distinct().order_by(Course.credits).all()
        departments = db.session.query(Course.department).distinct().order_by(Course.department).all()
        logger.info(f'Fetched {len(credits)} credit options and {len(departments)} department options')
        return jsonify({
            "success": True,
            "credits": [credit[0] for credit in credits],
            "departments": [dept[0] for dept in departments if dept[0]]  # None 값 제외
        }), 200
    except Exception as e:
        logger.error(f'Error occurred while fetching dropdown options: {str(e)}')
        return jsonify({"success": False, "message": "An error occurred while fetching dropdown options"}), 500

@course.route('/course_registration/credits')
@jwt_req_custom
def get_credits():
    logger.info('Redirecting to get_dropdown_options for credits')
    return redirect(url_for('course.get_dropdown_options'))

@course.route('/course_registration/departments')
@jwt_req_custom
def get_departments():
    logger.info('Redirecting to get_dropdown_options for departments')
    return redirect(url_for('course.get_dropdown_options'))



@course.route('/course_registration/search_courses')
@jwt_req_custom
def search_courses():
    logger.info('Searching courses')
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
        logger.info(f'Found {len(courses_list)} courses matching the search criteria')
        return jsonify({'success': True, 'courses': courses_list})
    except Exception as e:
        logger.error(f'Error occurred while searching courses: {str(e)}')
        return jsonify({"success": False, "message": "An error occurred while searching courses"}), 500

@course.route('/course_registration/apply_course', methods=['POST'])
@jwt_req_custom
def apply_course():
    data = request.get_json()
    course_key = data.get('course_key')
    user_id = get_current_user_id()  # This gets the user.id from JWT
    logger.info(f'Applying for course {course_key} for user {user_id}')

    try:
        # Get the student record using id (which is equivalent to user_id)
        student = Student.query.filter_by(id=user_id).first()
        if not student:
            logger.warning(f'Student not found for user {user_id}')
            return jsonify({"success": False, "message": "학생 정보를 찾을 수 없습니다."}), 404

        student_id = student.student_id  # Get the actual student_id
        
        course = Course.query.filter_by(course_key=course_key).first()
        if not course:
            logger.warning(f'Course not found: {course_key}')
            return jsonify({"success": False, "message": "과목을 찾을 수 없습니다."}), 404

        if course.current_students >= course.max_students:
            logger.info(f'Course {course_key} is full')
            return jsonify({"success": False, "message": "수강 인원이 꽉 찼습니다."}), 400

        existing_registration = Registration.query.filter_by(
            course_key=course_key, 
            student_id=student_id
        ).first()
        
        if existing_registration:
            if existing_registration.status == 'Applied':
                logger.info(f'Student {student_id} already applied for course {course_key}')
                return jsonify({"success": False, "message": "이미 신청한 과목입니다."}), 400
            elif existing_registration.status == 'Cancelled':
                # Update the existing registration to 'Applied'
                existing_registration.status = 'Applied'
                db.session.add(existing_registration)
            else:
                logger.error(f'Unknown registration status for student {student_id} and course {course_key}')
                return jsonify({"success": False, "message": "알 수 없는 등록 상태입니다."}), 500
        else:
            # Create a new registration
            new_registration = Registration(course_key=course_key, student_id=student_id, status='Applied')
            db.session.add(new_registration)
        
        # Increment current_students
        course.current_students += 1
        
        db.session.commit()
        logger.info(f'Successfully applied for course {course_key} for student {student_id}')
        return jsonify({"success": True, "message": "과목 신청이 완료되었습니다."}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error occurred while applying for course: {str(e)}')
        return jsonify({"success": False, "message": str(e)}), 500

@course.route('/course_registration/cancel_course', methods=['POST'])
@jwt_req_custom
def cancel_course():
    data = request.get_json()
    course_key = data.get('course_key')
    user_id = get_current_user_id()
    logger.info(f'Cancelling course {course_key} for user {user_id}')
    try:
        # Get the student record using id (which is equivalent to user_id)
        student = Student.query.filter_by(id=user_id).first()
        if not student:
            logger.warning(f'Student not found for user {user_id}')
            return jsonify({"success": False, "message": "학생 정보를 찾을 수 없습니다."}), 404

        student_id = student.student_id  # Get the actual student_id

        registration = Registration.query.filter_by(
            course_key=course_key, 
            student_id=student_id
        ).first()
        
        if not registration:
            logger.warning(f'Registration not found for student {student_id} and course {course_key}')
            return jsonify({"success": False, "message": "신청 내역을 찾을 수 없습니다."}), 404

        course = Course.query.filter_by(course_key=course_key).first()
        if not course:
            logger.warning(f'Course not found: {course_key}')
            return jsonify({"success": False, "message": "과목을 찾을 수 없습니다."}), 404

        db.session.delete(registration)
        
        # Decrement current_students
        course.current_students = max(0, course.current_students - 1)
        
        db.session.commit()
        logger.info(f'Successfully cancelled course {course_key} for student {student_id}')
        return jsonify({"success": True, "message": "과목 취소가 완료되었습니다."}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error occurred while cancelling course: {str(e)}')
        return jsonify({"success": False, "message": str(e)}), 500

@course.route('/course_registration/get_applied_courses', methods=['GET'])
@jwt_req_custom
def get_applied_courses():
    logger.info('Fetching applied courses')
    try:
        user_id = get_current_user_id()
        student = Student.query.filter_by(id=user_id).first()
        if not student:
            logger.warning(f'Student not found for user {user_id}')
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
        logger.info(f'Fetched {len(courses_data)} applied courses for user {user_id}')
        return jsonify({"success": True, "courses": courses_data}), 200

    except SQLAlchemyError as e:
        logger.error(f'Database error occurred while fetching applied courses: {str(e)}')
        return jsonify({"success": False, "message": "Database error occurred"}), 500
    except Exception as e:
        logger.error(f'Error occurred while fetching applied courses: {str(e)}')
        return jsonify({"success": False, "message": str(e)}), 500

@course.route('/main')
def main():
    logger.info('Redirecting to main page')
    return redirect('http://kangyk.com/main')

@course.route('/festival')
def festival():
    logger.info('Redirecting to festival page')
    return redirect('http://kangyk.com/festival')

@course.route('/notice')
def news():
    logger.info('Redirecting to news page')
    return redirect('http://kangyk.com/notice')

@course.route('/logout')
@jwt_req_custom
def logout():
    logger.info('User logging out')
    response = make_response(redirect('http://kangyk.com/login'))
    unset_jwt_cookies(response)
    return response

@course.route('/login')
def login():
    logger.info('Redirecting to login page')
    return redirect('http://kangyk.com/login')

