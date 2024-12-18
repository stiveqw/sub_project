import requests
import time
import random
import logging
from requests.exceptions import RequestException
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from flask import Flask, jsonify, make_response
from flask_jwt_extended import JWTManager, create_access_token, set_access_cookies, verify_jwt_in_request
from config import Config
from models import db, Course
from sqlalchemy.exc import SQLAlchemyError


# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Flask 앱 및 JWTManager 설정

app = Flask(__name__)
app.config.from_object(Config)
app.config['JWT_SECRET_KEY'] = 'jwt_secret_key'  # 실제 운영 환경에서는 안전하게 관리해야 합니다
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False  # 개발 환경에서는 False, 운영 환경에서는 True로 설정
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
jwt = JWTManager(app)

BASE_URL = "http://localhost:5001"  # 환경에 맞게 조정

used_ids = set()
used_student_ids = set()
used_emails = set()
used_phone_numbers = set()

id_student_id_map = {
    12: '20230001',
    13: '20230002',
    14: '20230003',
    15: '20230004',
    16: '20230005',
    17: '20230006',
    18: '20230007',
    19: '20230008',
    20: '20230009',
    21: '202300010',
    22: '20230011',
    23: '20230012',
    24: '20230013',
    25: '20230014',
    26: '20230015',
    27: '20230016',
    28: '20230017',
    29: '20230018',
    30: '20230019',
    31: '20230020',
    32: '20230021',
    33: '20230022',
    34: '20230023',
    35: '20230024',
    36: '20230025',
    37: '20230026',
    38: '20230027',
    39: '20230028',
    40: '20230029',
    41: '20230030',
    42: '20230031',
    43: '20230032',
    44: '20230033',
    45: '20230034',
    46: '20230035',
    47: '20230036',
    48: '20230037',
    49: '20230038',
    50: '20230039',
    51: '20230040',
    52: '20230041',
    53: '20230042',
    54: '20230043',
    55: '20230044',
    56: '20230045',
    57: '20230046',
    58: '20230047',
    59: '20230048',
    60: '20230049',
    61: '20230050',
    62: '20230051',
    63: '20230052',
    64: '20230053',
    65: '20230054',
    66: '20230055',
    67: '20230056',
    68: '20230057',
    69: '20230058',
    70: '20230059',
    71: '20230060',
    72: '20230061',
    73: '20230062',
    74: '20230063',
    75: '20230064',
    76: '20230065',
    77: '20230066',
    78: '20230067',
    79: '20230068',
    80: '20230069',
    81: '20230070',
    82: '20230071',
    83: '20230072',
    84: '20230073',
    85: '20230074',
    86: '20230075',
    87: '20230076',
    88: '20230077',
    89: '20230078',
    90: '20230079',
    91: '20230080',
    92: '20230081',
    93: '20230082',
    94: '20230083',
    95: '20230084',
    96: '20230085',
    97: '20230086',
    98: '20230087',
    99: '20230088',
    100: '20230089',
    101: '20230090',
    102: '20230091',
    103: '20230092'
}


def generate_student_data():
    attempts = 0
    while True:
        attempts += 1
        id = random.randint(12, 103)
        student_id = id_student_id_map[id]
        email = f"student{random.randint(1, 9999)}@example.com"
        phone_number = f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
        
        if id not in used_ids and student_id not in used_student_ids and \
           email not in used_emails and phone_number not in used_phone_numbers:
            used_ids.add(id)
            used_student_ids.add(student_id)
            used_emails.add(email)
            used_phone_numbers.add(phone_number)
            
            student_data = {
                "id": id,
                "student_id": student_id,
                "name": f"Student {random.randint(1, 100)}",
                "email": email,
                "phone_number": phone_number,
                "department": random.choice(["Computer Science", "Electrical Engineering", "Mechanical Engineering", "Business Administration"])
            }
            
            return student_data
        
        if attempts >= 1000:
            raise RuntimeError("Unable to generate unique student data")

def generate_jwt_token(user_id):
    logger.info(f"Attempting to generate JWT token for user_id: {user_id}")
    try:
        with app.app_context():
            access_token = create_access_token(identity=str(user_id))
        logger.info(f"JWT token successfully generated for user_id: {user_id}")
        logger.debug(f"Token preview: {access_token[:1]}...")
        return access_token
    except Exception as e:
        logger.error(f"JWT token generation failed: {str(e)}")
        logger.exception("Detailed traceback:")
        raise

def set_access_token_cookie(response, token):
    """
    응답 객체에 access_token_cookie를 설정합니다.
    """
    with app.app_context():
        set_access_cookies(response, token)
    logger.info("access_token_cookie가 응답 객체에 설정되었습니다.")

def get_student_with_token():
    try:
        student = random.choice(students)
        token = generate_jwt_token(student['id'])
        response = make_response(jsonify({'message': 'Token generated'}))
        set_access_token_cookie(response, token)
        return student, response
    except Exception as e:
        logger.error(f"Error in get_student_with_token: {str(e)}")
        raise

students = [generate_student_data() for _ in range(90)]

def check_system_health():
    logger.info("Starting system health check")
    try:
        logger.debug("Generating student with token")
        student, response = get_student_with_token()
        cookies = response.headers.get('Set-Cookie')
        logger.debug(f"Received cookies: {cookies}")
        headers = {'Cookie': cookies} if cookies else {}
        logger.info(f"Sending health check request to {BASE_URL}/api/search_courses")
        response = requests.get(f"{BASE_URL}/api/search_courses", headers=headers)
        
        if response.status_code == 200:
            logger.info("System health check successful")
            return True
        else:
            logger.error(f"System health check failed with status code: {response.status_code}")
            logger.debug(f"Response content: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Unexpected error during system health check: {str(e)}")
        logger.exception("Detailed traceback:")
        return False

def fetch_dropdown_options(headers):
    logger.info("Starting to fetch dropdown options")
    try:
        url = f"{BASE_URL}/api/dropdown_options"
        logger.debug(f"Sending GET request to {url}")
        logger.debug(f"Request headers: {headers}")
        
        response = requests.get(url, headers=headers, timeout=10)
        logger.debug(f"Received response with status code: {response.status_code}")
        logger.debug(f"Response headers: {response.headers}")
    
        if response.status_code == 200:
            try:
                data = response.json()
                logger.debug(f"Response data: {data}")
                
                if data.get("success"):
                    credits = data.get("credits")
                    departments = data.get("departments")
                    logger.info(f"Successfully fetched dropdown options. Credits: {credits}, Departments: {departments}")
                    return credits, departments
                else:
                    logger.warning(f"API request was successful, but 'success' flag in response was False. Message: {data.get('message', 'No message provided')}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {str(e)}")
                logger.error(f"Raw response content: {response.text}")
        else:
            logger.error(f"Failed to fetch dropdown options. Status code: {response.status_code}")
            logger.error(f"Response content: {response.text}")
        
        logger.error("Failed to fetch dropdown options")
        return None, None
    except RequestException as e:
        logger.error(f"Network error occurred while fetching dropdown options: {str(e)}")
        return None, None
    except Exception as e:
        logger.error(f"Unexpected error occurred while fetching dropdown options: {str(e)}")
        return None, None
        
def search_courses(headers, credits=None, department=None, course_name=None):
    params = {}
    if credits:
        params['credits'] = credits
    if department:
        params['department'] = department
    if course_name:
        params['course_name'] = course_name
    
    response = requests.get(f"{BASE_URL}/api/search_courses", params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            logger.info(f"Found {len(data.get('courses', []))} courses")
            return data.get("courses")
    logger.error("Failed to search courses")
    return []

def apply_course(headers, course_key):
    logger.info(f"Applying for course: {course_key}")
    response = requests.post(f"{BASE_URL}/api/apply_course", json={"course_key": course_key}, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            logger.info("Course application successful")
            return True
    logger.error("Course application failed")
    return False

def cancel_course(headers, course_key):
    logger.info(f"Cancelling course: {course_key}")
    response = requests.post(f"{BASE_URL}/api/cancel_course", json={"course_key": course_key}, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            logger.info("Course cancellation successful")
            return True
    logger.error("Course cancellation failed")
    return False



def simulate_course_registration(course_keys):
    logger.info("Starting course registration simulation")
    try:
        with app.app_context():
            student, response = get_student_with_token()
            cookies = response.headers.get('Set-Cookie')
            headers = {'Cookie': cookies} if cookies else {}

            if not course_keys:
                logger.error("No available courses found in the database")
                return False

            random.shuffle(course_keys)  # Randomize the order of course attempts

            for course_key in course_keys:
                logger.info(f"Attempting to apply for course: {course_key}")
                if apply_course(headers, course_key):
                    logger.info(f"Successfully applied for course: {course_key}")
                    time.sleep(random.uniform(0.5, 2))  # Simulate some time passing
                    if random.random() < 0.3:  # 30% chance to cancel the course
                        logger.info(f"Attempting to cancel course: {course_key}")
                        cancel_result = cancel_course(headers, course_key)
                        logger.info(f"Course cancellation result: {'Success' if cancel_result else 'Failed'}")
                    return True
                else:
                    logger.warning(f"Failed to apply for course: {course_key}, trying next course")

            logger.error("Failed to apply for any course")
            return False

    except Exception as e:
        logger.exception(f"Unexpected error in simulate_course_registration: {str(e)}")
        return False
    finally:
        logger.info("Course registration simulation completed")



def simulate_concurrent_registrations(num_concurrent, course_keys):
    logger.info(f"Starting simulation of {num_concurrent} concurrent course registrations")
    with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
        futures = [executor.submit(simulate_course_registration, course_keys) for _ in range(num_concurrent)]
        results = [future.result() for future in as_completed(futures)]
    
    successful_registrations = sum(results)
    logger.info(f"Concurrent registration test completed: {successful_registrations}/{num_concurrent} successful")
    return successful_registrations == num_concurrent

def inject_network_delay(headers):
    logger.info("Injecting network delay...")
    original_get = requests.get
    original_post = requests.post

    def delayed_request(method, *args, **kwargs):
        time.sleep(random.uniform(1, 3))  # Random delay between 1 and 3 seconds
        return method(*args, **kwargs)

    requests.get = lambda *args, **kwargs: delayed_request(original_get, *args, **kwargs)
    requests.post = lambda *args, **kwargs: delayed_request(original_post, *args, **kwargs)

    # Test the delay
    start_time = time.time()
    fetch_dropdown_options(headers)
    end_time = time.time()

    requests.get = original_get
    requests.post = original_post

    if end_time - start_time > 1:
        logger.info("Network delay injection successful")
        return True
    else:
        logger.error("Network delay injection failed")
        return False

#def simulate_high_load():
    logger.info("Simulating high load...")
    num_requests = 10
    successful_requests = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(simulate_course_registration) for _ in range(num_requests)]
        results = [future.result() for future in as_completed(futures)]
    
    successful_requests = sum(1 for result in results if result)
    logger.info(f"High load test: {successful_requests}/{num_requests} successful")
    return successful_requests > num_requests * 0.8  # Consider success if 80% of requests succeed

def wait_for_recovery(timeout=30, interval=5):
    logger.info(f"Waiting for system to recover (timeout: {timeout}s)...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        if check_system_health():
            logger.info("System recovered successfully")
            return True
        time.sleep(interval)
    logger.error("System failed to recover within the timeout period")
    return False

def run_chaos_experiment():
    logger.info("Starting chaos engineering experiment for course_service")
    course_keys = ['CSE101', 'MAT201', 'PHY301', 'CHE102', 'BIO202']
    num_concurrent = 200
    with app.app_context():
        if not check_system_health():
            logger.error("System is not healthy at the start. Aborting experiment.")
            return
        
        # Test 1: Concurrent Registrations
        if not simulate_concurrent_registrations(num_concurrent, course_keys):
            logger.error("System failed to handle concurrent registrations properly")
            if not wait_for_recovery():
                return

        # Test 2: Network Delay
        student, response = get_student_with_token()
        cookies = response.headers.get('Set-Cookie')
        headers = {'Cookie': cookies} if cookies else {}

        if inject_network_delay(headers):
            if not wait_for_recovery():
                logger.error("System failed to recover from network delay")
                return

        # Test 3: High Load
        #if not simulate_high_load():
        #    logger.error("System failed under high load")
        #    if not wait_for_recovery():
        #        return

        if check_system_health():
            logger.info("System remained healthy after all experiments. Chaos engineering test passed!")
        else:
            logger.error("System health check failed after experiments. Further investigation needed.")

if __name__ == "__main__":
    run_chaos_experiment()

