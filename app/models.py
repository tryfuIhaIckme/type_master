from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # система ролей
    
    # связь 1 - n (чтоби много сессий сделать для юзера)
    sessions = db.relationship('TestSession', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Text(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(10), default='en')
    difficulty = db.Column(db.String(20), default='easy')

class TestSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text_id = db.Column(db.Integer, db.ForeignKey('text.id'), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # связь 1-к-1 с результатом
    result = db.relationship('Result', backref='session', uselist=False)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('test_session.id'), unique=True)
    wpm = db.Column(db.Integer, nullable=False)
    accuracy = db.Column(db.Float, nullable=False)
    errors_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)