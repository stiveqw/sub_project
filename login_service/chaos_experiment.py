import requests
import threading
import time
import random
import logging
import itertools
import string
from faker import Faker
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import timedelta
from flask import Flask, jsonify, make_response
from flask_jwt_extended import JWTManager, create_access_token, set_access_cookies


fake = Faker()

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Flask 앱 및 JWTManager 설정
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'jwt_secret_key'  
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False  
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
jwt = JWTManager(app)

LOGIN_SERVICE_URL = "http://localhost:5006"
MAIN_SERVICE_URL = "http://localhost:5003"

login_student_id_iterator = itertools.count(start=20231001)
login_user_id_iterator = itertools.count(start=1)

register_student_id_iterator = itertools.count(start=20231202)
register_user_id_iterator = itertools.count(start=202)

def generate_user_data_for_login():
    user_id = next(login_user_id_iterator)
    student_id = next(login_student_id_iterator)
    if student_id > 20231201:
        raise StopIteration("Maximum number of users reached")
    
    return {
        "user_id": user_id,
        "student_id": str(student_id),
        "department": ''.join(filter(str.isalnum, fake.job()))[:100],
        "name": ''.join(filter(str.isalnum, fake.name()))[:100],
        "email": f"{student_id}@example.com",
        "phone_number": f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
        "password": "testpassword123"  # 모든 사용자에게 동일한 간단한 비밀번호 할당
    }

def generate_user_data_for_registration():
    user_id = next(register_user_id_iterator)
    student_id = next(register_student_id_iterator)
    
    if user_id > (202 + 200):
        raise StopIteration("Maximum number of registration users reached")
    
    # 랜덤 비밀번호 생성 (8-12자리, 영문 대소문자, 숫자, 특수문자 포함)
    password = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=random.randint(8, 12)))
    
    return {
        "user_id": user_id,
        "student_id": str(student_id),
        "department": fake.job()[:100],  # 100자 이내로 제한
        "name": fake.name()[:100],  # 100자 이내로 제한
        "email": f"{student_id}@example.com",
        "phone_number": f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
        "password": password
    }

def generate_jwt_token(user_id):
    logger.info(f"Attempting to generate JWT token for user_id: {user_id}")
    try:
        with app.app_context():
            access_token = create_access_token(identity=str(user_id))
        logger.info(f"JWT token successfully generated for user_id: {user_id}")
        logger.debug(f"Token preview: {access_token[:3]}...")
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

def register_user(user_data):
    try:
        response = requests.post(f"{LOGIN_SERVICE_URL}/register", data=user_data)
        return response.status_code == 201
    except requests.RequestException as e:
        logger.error(f"Registration error: {e}")
        return False

def login_user(user_data):
    logger.info(f"Attempting login for user with student_id: {user_data['student_id']}")
    try:
        response = requests.post(f"{LOGIN_SERVICE_URL}/login", data={
            "student_id": user_data["student_id"],
            "password": user_data["password"]
        })
        if response.status_code == 200:
            logger.info(f"Login successful for user {user_data['student_id']}")
            response_data = response.json()
            if response_data.get('success'):
                # 서버에서 제공한 리다이렉트 URL로 접근
                redirect_url = response_data.get('redirect_url')
                cookies = response.cookies  # 서버에서 설정한 쿠키 사용
                main_response = requests.get(redirect_url, cookies=cookies)
                if main_response.status_code == 200:
                    logger.info(f"Main service access successful for user {user_data['student_id']}")
                    return True
                else:
                    logger.warning(f"Main service access failed for user {user_data['student_id']}. Status code: {main_response.status_code}")
            else:
                logger.warning(f"Login failed for user {user_data['student_id']}: {response_data.get('message')}")
        else:
            logger.warning(f"Login failed for user {user_data['student_id']}. Status code: {response.status_code}")
        return False
    except requests.RequestException as e:
        logger.error(f"Login error for user {user_data['student_id']}: {str(e)}")
        return False


def access_page(url, cookies=None):
    try:
        headers = {'Cookie': cookies} if cookies else {}
        response = requests.get(url, headers=headers)
        return response.status_code == 200
    except requests.RequestException as e:
        logger.error(f"Page access error: {e}")
        return False

def run_chaos_test(num_users=200):
    
    login_users = []
    register_users = []

     # 로그인용 사용자 생성
    for _ in range(min(num_users, 201)):  # 최대 201명까지만 생성 (기존 사용자)
        try:
            login_users.append(generate_user_data_for_login())
        except StopIteration:
            break
    
    # 회원가입용 사용자 생성
    for _ in range(num_users):
        try:
            register_users.append(generate_user_data_for_registration())
        except StopIteration:
            break
    
    # 모든 작업을 하나의 리스트에 추가
 # 태스크 생성
    tasks = []
    
    # 회원가입 태스크
    for user in register_users:
        tasks.append(('register', user))
    
    # 로그인 태스크
    for user in login_users:
        tasks.append(('login', user))

    for _ in range(num_users * 2):  # 각 사용자당 평균 2번의 페이지 접근
        tasks.append(('access', (random.choice([f"{LOGIN_SERVICE_URL}/login", f"{LOGIN_SERVICE_URL}/register"]), None)))
    
    random.shuffle(tasks)  # 작업 순서를 무작위로 섞음
    
    results = {'register': 0, 'login': 0, 'access': 0}
    total_tasks = len(tasks)
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        future_to_task = {executor.submit(perform_task, task_type, data): (task_type, data) for task_type, data in tasks}
        for future in as_completed(future_to_task):
            task_type, _ = future_to_task[future]
            if future.result():
                results[task_type] += 1
    
    logger.info(f"Successful registrations: {results['register']}/{num_users}")
    logger.info(f"Successful logins: {results['login']}/{num_users}")
    logger.info(f"Successful page accesses: {results['access']}/{num_users * 2}")
    logger.info(f"Total successful tasks: {sum(results.values())}/{total_tasks}")

def perform_task(task_type, data):
    if task_type == 'register':
        return register_user(data)
    elif task_type == 'login':
        return login_user(data)
    elif task_type == 'access':
        url, cookies = data
        return access_page(url, cookies)

if __name__ == "__main__":
    start_time = time.time()
    run_chaos_test()
    end_time = time.time()
    logger.info(f"Total execution time: {end_time - start_time:.2f} seconds")

