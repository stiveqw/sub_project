from flask import Flask, jsonify, request, render_template, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, unset_jwt_cookies
from config import Config
from models import db, Notice

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
jwt = JWTManager(app)

@app.route('/')
def home():
    return redirect(url_for('news'))

@app.route('/notices', methods=['GET'])
def get_notices():
    notices = Notice.query.all()
    return jsonify([{'id': n.id, 'title': n.title, 'content': n.content, 'date': n.date} for n in notices])

@app.route('/notices', methods=['POST'])
@jwt_required()
def create_notice():
    data = request.json
    new_notice = Notice(title=data['title'], content=data['content'], date=data['date'])
    db.session.add(new_notice)
    db.session.commit()
    return jsonify({'id': new_notice.id, 'title': new_notice.title, 'content': new_notice.content, 'date': new_notice.date}), 201

@app.route('/news')
def news():
    return render_template('news_main.html')

@app.route('/redirect_to_main')
def redirect_to_main():
    return redirect('http://localhost:5003/')  # main_service의 주소

@app.route('/redirect_to_festival')
def redirect_to_festival():
    return redirect('http://localhost:5002/')  # festival_service의 주소

@app.route('/redirect_to_course')
def redirect_to_course():
    return redirect('http://localhost:5001/course_registration')  # course_service의 주소

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    response = make_response(redirect('http://localhost:5006/login'))
    unset_jwt_cookies(response)
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)

