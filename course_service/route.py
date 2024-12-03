from flask import jsonify, url_for, redirect
from flask_jwt_extended import jwt_required, verify_jwt_in_request

def init_routes(app):
    @app.route('/')
    @jwt_required()
    def index():
        try:
            verify_jwt_in_request()
            return "Welcome to the Course Service"
        except Exception as e:
            return jsonify({"error": "로그인이 필요한 서비스입니다.", "redirect": url_for('login', _external=True)}), 401

    @app.route('/login')
    def login():
        return redirect('http://localhost:5006/login')

