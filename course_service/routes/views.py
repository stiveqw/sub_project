from flask import render_template, redirect, url_for, request, jsonify, make_response, current_app
from flask_jwt_extended import jwt_required, unset_jwt_cookies, get_jwt_identity, verify_jwt_in_request
from werkzeug.exceptions import Unauthorized, UnprocessableEntity
from . import course
from functools import wraps
from models import db, Course, Registration, Student
from sqlalchemy.exc import SQLAlchemyError
from config import Config
from flask import Flask
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)



TEST_USER_ID = 99

#재시도 함수
def retry_on_exception(max_retries=3, backoff_factor=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except SQLAlchemyError as e:
                    retries += 1
                    if retries == max_retries:
                        raise
                    wait_time = backoff_factor ** retries
                    logger.warning(f"Retry {retries}/{max_retries} after {wait_time} seconds due to: {str(e)}")
                    time.sleep(wait_time)
        return wrapper
    return decorator
#jwt 인증 커스텀
def jwt_req_custom(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not app.config['TESTING']:
            verify_jwt_in_request()
        else:
            verify_jwt_in_request(optional=True)
        return fn(*args, **kwargs)
    return wrapper

def get_current_user_id():
    if app.config['TESTING']:
        return TEST_USER_ID
    return get_jwt_identity()

@course.route('/api/get_courses', methods=['GET'])
@jwt_req_custom
def get_courses():
   
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
        
        return jsonify({
            "success": True, 
            "courses": courses_data,
            "appliedCourses": applied_courses_data
        }), 200
    except Exception as e:
       
        return jsonify({"success": False, "message": "An error occurred while fetching courses"}), 500

@course.route('/course_registration')
@jwt_req_custom
def course_service():
    return render_template('course_service.html')

@course.route('/api/dropdown_options', methods=['GET'])
@jwt_required(optional=True)
def get_dropdown_options():
   
    try:
        credits = db.session.query(Course.credits).distinct().order_by(Course.credits).all()
        departments = db.session.query(Course.department).distinct().order_by(Course.department).all()
        
        return jsonify({
            "success": True,
            "credits": [credit[0] for credit in credits],
            "departments": [dept[0] for dept in departments if dept[0]]  # None 값 제외
        }), 200
    except Exception as e:
        
        return jsonify({"success": False, "message": "An error occurred while fetching dropdown options"}), 500

@course.route('/api/credits')
def get_credits():
    
    return redirect(url_for('course.get_dropdown_options'))

@course.route('/api/departments')
def get_departments():
   
    return redirect(url_for('course.get_dropdown_options'))



@course.route('/api/search_courses')
def search_courses():
    logger.info("Received request to /api/search_courses")   
    try:
        credits = request.args.get('credits')
        department = request.args.get('department')
        course_name = request.args.get('course_name')
        logger.debug(f"Search parameters - credits: {credits}, department: {department}, course_name: {course_name}")
        query = Course.query

        if credits and credits != 'Select Credits':
            query = query.filter(Course.credits == int(credits))
            logger.debug(f"Filtering by credits: {credits}")
        if department and department != 'Select Department':
            query = query.filter(Course.department == department)
            logger.debug(f"Filtering by department: {department}")
        if course_name:
            query = query.filter(Course.course_name.ilike(f'%{course_name}%'))
            logger.debug(f"Filtering by course name: {course_name}")

        courses = query.all()
        logger.info(f"Found {len(courses)} courses matching the criteria")
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
        logger.debug("Successfully serialized course data")
        return jsonify({'success': True, 'courses': courses_list})
    except ValueError as ve:
        logger.error(f"ValueError in search_courses: {str(ve)}")
        return jsonify({"success": False, "message": "Invalid input parameter"}), 400
    except SQLAlchemyError as se:
        logger.error(f"Database error in search_courses: {str(se)}")
        return jsonify({"success": False, "message": "Database error occurred"}), 500
    except Exception as e:
        logger.exception(f"Unexpected error in search_courses: {str(e)}")
        return jsonify({"success": False, "message": "An unexpected error occurred"}), 500

@course.route('/api/apply_course', methods=['POST'])
@jwt_required()
def apply_course():
    logger.info("Received request to /api/apply_course")
    data = request.get_json()
    course_key = data.get('course_key')
    user_id = get_jwt_identity()

    logger.debug(f"Applying for course: {course_key}, User ID: {user_id}")

    try:
        student = Student.query.filter_by(id=user_id).first()
        if not student:
            logger.error(f"No student found for user ID: {user_id}")
            return jsonify({"success": False, "message": "학생 정보를 찾을 수 없습니다."}), 404

        @retry_on_exception(max_retries=3, backoff_factor=2)
        def process_application():
            try:
                # 세션 초기화
                db.session.remove()
                db.session.begin()

                course = Course.query.filter_by(course_key=course_key).with_for_update().first()
                if not course:
                    logger.error(f"No course found with course_key: {course_key}")
                    return jsonify({"success": False, "message": "과목을 찾을 수 없습니다."}), 404

                if course.current_students >= course.max_students:
                    logger.warning(f"Course {course_key} is full. Current: {course.current_students}, Max: {course.max_students}")
                    return jsonify({"success": False, "message": "수강 인원이 꽉 찼습니다."}), 400

                existing_registration = Registration.query.filter_by(
                    course_key=course_key, 
                    student_id=student.student_id
                ).first()
                
                if existing_registration:
                    if existing_registration.status == 'Applied':
                        logger.warning(f"Student {student.student_id} has already applied for course {course_key}")
                        return jsonify({"success": False, "message": "이미 신청한 과목입니다."}), 400
                    elif existing_registration.status == 'Cancelled':
                        existing_registration.status = 'Applied'
                        logger.info(f"Updated cancelled registration to 'Applied' for student {student.student_id}, course {course_key}")
                    else:
                        logger.error(f"Unknown registration status for student {student.student_id}, course {course_key}: {existing_registration.status}")
                        return jsonify({"success": False, "message": "알 수 없는 등록 상태입니다."}), 500
                else:
                    new_registration = Registration(course_key=course_key, student_id=student.student_id, status='Applied')
                    db.session.add(new_registration)
                    logger.info(f"Created new registration for student {student.student_id}, course {course_key}")
                
                course.current_students += 1
                logger.info(f"Incremented current_students for course {course_key}: {course.current_students}")

                db.session.commit()
                logger.info("Transaction committed successfully")
                return jsonify({"success": True, "message": "과목 신청이 완료되었습니다."}), 200

            except SQLAlchemyError as e:
                db.session.rollback()
                logger.exception(f"Database error in process_application: {str(e)}")
                raise
            finally:
                db.session.close()

        return process_application()

    except SQLAlchemyError as e:
        logger.exception(f"Database error in apply_course: {str(e)}")
        return jsonify({"success": False, "message": "과목 신청 중 데이터베이스 오류가 발생했습니다."}), 500
    except Exception as e:
        logger.exception(f"Unexpected error in apply_course: {str(e)}")
        return jsonify({"success": False, "message": "과목 신청 중 예기치 못한 오류가 발생했습니다."}), 500

@course.route('/api/cancel_course', methods=['POST'])
@jwt_req_custom
def cancel_course():
    logger.info("Received request to /api/cancel_course")
    data = request.get_json()
    course_key = data.get('course_key')
    user_id = get_current_user_id()
    logger.debug(f"Cancelling course: {course_key}, User ID: {user_id}")
    try:
        with db.session.begin():
        # Get the student record using id (which is equivalent to user_id)
            student = Student.query.filter_by(id=user_id).first()
            if not student:
                logger.error(f"No student found for user ID: {user_id}")
                return jsonify({"success": False, "message": "학생 정보를 찾을 수 없습니다."}), 404

            student_id = student.student_id  # Get the actual student_id
            logger.debug(f"Found student with student_id: {student_id}")
            registration = Registration.query.filter_by(
                course_key=course_key, 
                student_id=student_id
            ).with_for_update().first()
            
            if not registration:
                logger.error(f"No registration found for student {student_id}, course {course_key}")
                return jsonify({"success": False, "message": "신청 내역을 찾을 수 없습니다."}), 404
            if registration.status == 'Cancelled':
                return jsonify({"success": False, "message": "과목을 찾을 수 없습니다."}), 404
            registration.status = 'Cancelled'
            logger.info(f"Deleted registration for student {student_id}, course {course_key}")
            # Decrement current_students
            # Update the Course table
            course = Course.query.filter_by(course_key=course_key).first()
            if course:
                course.current_students = max(0, course.current_students - 1)
                logger.debug(f"Updated current_students for course {course_key}: {course.current_students}")
            db.session.commit()
            return jsonify({"success": True, "message": "과목 취소가 완료되었습니다."}), 200
    except SQLAlchemyError as e:
        logger.exception(f"Database error in cancel_course: {str(e)}")
        return jsonify({"success": False, "message": "과목 취소 중 데이터베이스 오류가 발생했습니다."}), 500
    except Exception as e:
        logger.exception(f"Unexpected error in cancel_course: {str(e)}")
        return jsonify({"success": False, "message": "과목 취소 중 예기치 못한 오류가 발생했습니다."}), 500

@course.route('/api/get_applied_courses', methods=['GET'])
@jwt_req_custom
def get_applied_courses():
   
    try:
        user_id = get_current_user_id()
        
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
   
    return redirect('kangyk.com/main')

@course.route('/redirect_to_festival')
def redirect_to_festival():
   
    return redirect('http://kangyk.com/festival')

@course.route('/redirect_to_news')
def redirect_to_news():
   
    return redirect('http://kangyk.com/notice')

@course.route('/logout')
@jwt_req_custom
def logout():
  
    response = make_response(redirect('http://kangyk.com/login'))
    unset_jwt_cookies(response)
    return response

@course.route('/login')
def login():
    return redirect('http://kangyk.com/login')

