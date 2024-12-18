from functools import wraps
from flask import render_template, redirect, url_for, request, jsonify, make_response, current_app
from flask_jwt_extended import jwt_required, unset_jwt_cookies, verify_jwt_in_request
from models import Notice, db
from . import notice

def jwt_optional(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_app.config['TESTING']:
            try:
                verify_jwt_in_request(optional=True)
            except Exception as e:
                pass
        return f(*args, **kwargs)
    return wrapper

@notice.route('/news')
@jwt_optional
def news():
    notices = Notice.query.order_by(Notice.date.desc()).all()
    return render_template('news_main.html', notices=notices)

@notice.route('/news/<int:notice_id>')
@jwt_optional
def news_item(notice_id):
    notice = Notice.query.get_or_404(notice_id)
    return render_template('news_item.html', notice=notice)

@notice.route('/redirect_to_main')
def redirect_to_main():
    return redirect('http://kangyk.com/main')

@notice.route('/redirect_to_festival')
def redirect_to_festival():
    return redirect('http://kangyk.com/festival')

@notice.route('/redirect_to_course')
def redirect_to_course():
    return redirect('http://kangyk.com/course_registration')

@notice.route('/logout')
@jwt_optional
def logout():
    response = make_response(redirect('http://kangyk.com/login'))
    unset_jwt_cookies(response)
    return response

@notice.route('/login')
def login():
    return redirect('http://kangyk.com/login')

@notice.route('/api/notices')
def get_notices():
    notices = Notice.query.order_by(Notice.date.desc()).all()
    return jsonify([{
        'id': notice.id,
        'title': notice.title,
        'content': notice.content,
        'date': notice.date.isoformat()
    } for notice in notices])

