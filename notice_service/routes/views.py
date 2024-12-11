from flask import render_template, redirect, url_for, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, unset_jwt_cookies
from functools import wraps
import logging
from models import Notice, db
from . import notice



@notice.route('/')
@jwt_required()
def home():
    try:
        verify_jwt_in_request()
        return redirect(url_for('notice.news'))
    except Exception as e:
        return jsonify({"error": "로그인이 필요한 서비스입니다.", "redirect": url_for('notice.login', _external=True)}), 401

@notice.route('/news')
@jwt_required()
def news():
    notices = Notice.query.order_by(Notice.date.desc()).all()
    return render_template('news_main.html', notices=notices)

@notice.route('/news/<int:notice_id>')
@jwt_required()
def news_item(notice_id):
    notice = Notice.query.get_or_404(notice_id)
    return render_template('news_item.html', notice=notice)

@notice.route('/redirect_to_main')
def redirect_to_main():
    return redirect('http://localhost:5003/')

@notice.route('/redirect_to_festival')
def redirect_to_festival():
    return redirect('http://localhost:5002/')

@notice.route('/redirect_to_course')
def redirect_to_course():
    return redirect('http://localhost:5001/course_registration')

@notice.route('/logout')
@jwt_required()
def logout():
    response = make_response(redirect('http://localhost:5006/login'))
    unset_jwt_cookies(response)
    return response

@notice.route('/login')
def login():
    return redirect('http://localhost:5006/login')

@notice.route('/api/notices')
def get_notices():
    notices = Notice.query.order_by(Notice.date.desc()).all()
    return jsonify([{
        'id': notice.id,
        'title': notice.title,
        'content': notice.content,
        'date': notice.date.isoformat()
    } for notice in notices])

