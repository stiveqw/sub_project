from flask import Flask, render_template, redirect, url_for
from config import Config
import logging

app = Flask(__name__)
app.config.from_object(Config)

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/unauthorized')
def unauthorized():
    logger.info("Unauthorized access attempt")
    return render_template('unauthorized.html'), 401

@app.route('/not_found')
def not_found():
    logger.info("Page not found")
    return render_template('not_found.html'), 404

@app.route('/redirect_to_login')
def redirect_to_login():
    logger.info("Redirecting to login page")
    return redirect('http://localhost:5006/login')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)

