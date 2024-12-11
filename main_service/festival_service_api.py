import requests
from flask import current_app
from flask_jwt_extended import get_jwt

   .get  (__name__)

class FestivalServiceAPI:
    @staticmethod
    def get_festivals():
        try:
            festival_service_url = current_app.config['FESTIVAL_SERVICE_URL']
            full_url = f"{festival_service_url}/api/festivals"
              .info(f"Attempting to fetch festivals from: {full_url}")
            
            # Get the JWT token
            jwt_token = get_jwt()
            if not jwt_token:
                  .error("JWT token not found")
                return {"success": False, "error": "Authentication token not found"}

            headers = {'Authorization': f'Bearer {jwt_token}'}
              .debug(f"Request headers: {headers}")
            
            response = requests.get(full_url, headers=headers, timeout=10)
              .debug(f"Response status code: {response.status_code}")
              .debug(f"Response headers: {response.headers}")
              .debug(f"Response content: {response.text}")
            
            response.raise_for_status()
            
            data = response.json()
              .info(f"Successfully fetched festivals. Response: {data}")
            
            return {"success": True, "festivals": data.get('festivals', [])}
        except requests.exceptions.RequestException as e:
              .error(f"Error fetching festivals from Festival Service: {str(e)}")
            if isinstance(e, requests.exceptions.ConnectionError):
                error_message = "Connection error. Is the Festival Service running?"
            elif isinstance(e, requests.exceptions.Timeout):
                error_message = "Request timed out. Festival Service might be slow or unresponsive."
            elif isinstance(e, requests.exceptions.HTTPError):
                error_message = f"HTTP error occurred. Status code: {e.response.status_code}"
                  .error(f"Response content: {e.response.text}")
            else:
                error_message = "An unexpected error occurred while fetching festivals."
            return {"success": False, "error": error_message}
        except ValueError as e:
              .error(f"JSON decoding error: {str(e)}")
            return {"success": False, "error": "Invalid JSON response from Festival Service"}
        except Exception as e:
              .exception(f"Unexpected error in get_festivals: {str(e)}")
            return {"success": False, "error": str(e)}

