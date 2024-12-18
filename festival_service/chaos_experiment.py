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

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Flask 앱 및 JWTManager 설정
app = Flask(__name__)
app.config.from_object(Config)
app.config['JWT_SECRET_KEY'] = 'jwt_secret_key'  
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False  
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
jwt = JWTManager(app)

BASE_URL = "http://localhost:5002"  # festival_service의 URL

used_ids = set()

def generate_user_data():
    attempts = 0
    while True:
        attempts += 1
        id = random.randint(7, 107)
        
        if id not in used_ids:
            used_ids.add(id)

            user_data = {
                "id": id,
            }
            
            return user_data
        if attempts >= 1000:
            raise RuntimeError("Unable to generate unique student data")

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

def get_user_with_token():
    try:
        user = random.choice(users)
        with app.app_context():
            token = generate_jwt_token(user['id'])
            response = make_response(jsonify({'message': 'Token generated'}))
            set_access_token_cookie(response, token)
        return user, response
    except Exception as e:
        logger.error(f"Error in get_user_with_token: {str(e)}")
        raise

users = [generate_user_data() for _ in range(100)]


def check_system_health():
    logger.info("Starting system health check")
    try:
        user, response = get_user_with_token()
        cookies = response.headers.get('Set-Cookie')
        headers = {'Cookie': cookies} if cookies else {}
        response = requests.get(f"{BASE_URL}/api/festivals", headers=headers)
        
        if response.status_code == 200:
            logger.info("System health check successful")
            return True
        else:
            logger.error(f"System health check failed with status code: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Unexpected error during system health check: {str(e)}")
        return False

def apply_festival(headers, festival_key, seat_number):
    logger.info(f"Applying for festival: {festival_key}, seat: {seat_number}")
    response = requests.post(f"{BASE_URL}/api/apply", json={"festival_key": festival_key, "seat_number": seat_number}, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            logger.info("Festival application successful")
            return True
        else:
            logger.warning(f"Festival application failed: {data.get('message')}")
            return False
    elif response.status_code == 400:
        data = response.json()
        if "이미 예약된 좌석입니다" in data.get('message', ''):
            logger.warning("Seat already reserved")
        elif "이미 이 축제에 예약하셨습니다" in data.get('message', ''):
            logger.warning("User already has a reservation for this festival")
        elif "축제가 이미 만석입니다" in data.get('message', ''):
            logger.warning("Festival is full")
        else:
            logger.warning(f"Application failed: {data.get('message')}")
        return False
    elif response.status_code == 404:
        logger.error("Festival not found")
        return False
    else:
        logger.error(f"Unexpected error: Status code {response.status_code}")
        return False

def cancel_reservation(headers, reservation_id):
    logger.info(f"Cancelling reservation: {reservation_id}")
    response = requests.post(f"{BASE_URL}/api/cancel_reservation/{reservation_id}", headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            logger.info("Reservation cancellation successful")
            return True
    logger.error("Reservation cancellation failed")
    return False

def format_seat_number(seat_index):
    row = chr(ord('A') + (seat_index - 1) // 30)
    number = ((seat_index - 1) % 30) + 1
    return f"{row}{number}"

def get_all_festivals(headers):
    logger.info("Fetching all festivals")
    response = requests.get(f"{BASE_URL}/api/festivals", headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get("festivals", [])
    logger.error("Failed to fetch festivals")
    return []

def simulate_festival_reservation():
    logger.info("Starting festival reservation simulation")
    try:
        with app.app_context():
            user, response = get_user_with_token()
            cookies = response.headers.get('Set-Cookie')
            headers = {'Cookie': cookies} if cookies else {}

            all_festivals = get_all_festivals(headers)
            if not all_festivals:
                logger.error("No available festivals found")
                return False

            # Shuffle the festivals to randomize the order of attempts
            random.shuffle(all_festivals)

            for festival in all_festivals:
                total_seats = festival.get('total_seats', 90)
                seat_index = random.randint(1, total_seats)
                seat_number = format_seat_number(seat_index)

                logger.info(f"Attempting to apply for festival: {festival['festival_key']}, seat: {seat_number}")
                result = apply_festival(headers, festival['festival_key'], seat_number)
                
                if result:
                    logger.info(f"Successfully applied for festival: {festival['festival_key']}")
                    
                    # 30% chance to cancel the reservation
                    if random.random() < 0.3:
                        # Fetch user's reservations to get the reservation ID
                        response = requests.get(f"{BASE_URL}/api/festivals", headers=headers)
                        if response.status_code == 200:
                            user_reservations = response.json().get("user_reserved_festivals", [])
                            for reservation in user_reservations:
                                if reservation['festival_key'] == festival['festival_key']:
                                    cancel_result = cancel_reservation(headers, reservation['id'])
                                    logger.info(f"Reservation cancellation result: {'Success' if cancel_result else 'Failed'}")
                                    break
                    return True
                else:
                    logger.warning(f"Failed to apply for festival: {festival['festival_key']}")
                    
                    # If the application failed, we can try a different seat in the same festival
                    for _ in range(3):  # Try up to 3 more times with different seats
                        seat_index = random.randint(1, total_seats)
                        seat_number = format_seat_number(seat_index)
                        logger.info(f"Retrying with a different seat: {seat_number}")
                        result = apply_festival(headers, festival['festival_key'], seat_number)
                        if result:
                            logger.info(f"Successfully applied for festival: {festival['festival_key']} on retry")
                            
                            # 30% chance to cancel the reservation
                            if random.random() < 0.3:
                                # Fetch user's reservations to get the reservation ID
                                response = requests.get(f"{BASE_URL}/api/festivals", headers=headers)
                                if response.status_code == 200:
                                    user_reservations = response.json().get("user_reserved_festivals", [])
                                    for reservation in user_reservations:
                                        if reservation['festival_key'] == festival['festival_key']:
                                            cancel_result = cancel_reservation(headers, reservation['id'])
                                            logger.info(f"Reservation cancellation result: {'Success' if cancel_result else 'Failed'}")
                                            break
                            return True
                    
                    # If all retries for this festival failed, move to the next festival
                    logger.warning(f"All attempts failed for festival: {festival['festival_key']}")

            logger.warning("Failed to apply for any festival after trying all options")
            return False

    except Exception as e:
        logger.exception(f"Unexpected error in simulate_festival_reservation: {str(e)}")
        return False
    
def simulate_concurrent_reservations(num_concurrent):
    logger.info(f"Starting simulation of {num_concurrent} concurrent festival reservations")
    with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
        futures = [executor.submit(simulate_festival_reservation) for _ in range(num_concurrent)]
        results = [future.result() for future in as_completed(futures)]
    
    successful_reservations = sum(results)
    logger.info(f"Concurrent reservation test completed: {successful_reservations}/{num_concurrent} successful")
    return successful_reservations == num_concurrent

def inject_network_delay():
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
    check_system_health()
    end_time = time.time()

    requests.get = original_get
    requests.post = original_post

    if end_time - start_time > 1:
        logger.info("Network delay injection successful")
        return True
    else:
        logger.error("Network delay injection failed")
        return False

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
    logger.info("Starting chaos engineering experiment for festival_service")
    num_concurrent = 200

    if not check_system_health():
        logger.error("System is not healthy at the start. Aborting experiment.")
        return
    
    # Test 1: Concurrent Reservations
    if not simulate_concurrent_reservations(num_concurrent):
        logger.error("System failed to handle concurrent reservations properly")
        if not wait_for_recovery():
            return

    # Test 2: Network Delay
    if inject_network_delay():
        if not wait_for_recovery():
            logger.error("System failed to recover from network delay")
            return

    if check_system_health():
        logger.info("System remained healthy after all experiments. Chaos engineering test passed!")
    else:
        logger.error("System health check failed after experiments. Further investigation needed.")

if __name__ == "__main__":
    run_chaos_experiment()