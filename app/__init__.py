from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate

import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-123-replace-this-in-prod')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
migrate = Migrate(app, db)

from app import routes, models

# Создание таблиц и админа при запуске
with app.app_context():
    db.create_all()
    
    # Сбрасываем флаг админа у всех, кроме nikolaev
    models.User.query.filter(models.User.username != 'nikolaev').update({models.User.is_admin: False})
    
    # Ищем пользователя по имени ИЛИ по email, чтобы избежать конфликтов уникальности
    admin = models.User.query.filter(
        (models.User.username == 'nikolaev') | 
        (models.User.email == 'admin@typemaster.com')
    ).first()

    if not admin:
        hashed_password = bcrypt.generate_password_hash('nikolaev').decode('utf-8')
        admin = models.User(username='nikolaev', email='admin@typemaster.com', 
                            password_hash=hashed_password, is_admin=True)
        db.session.add(admin)
    else:
        # Обновляем существующего пользователя до нужных параметров админа
        admin.username = 'nikolaev'
        admin.email = 'admin@typemaster.com'
        admin.is_admin = True
        admin.password_hash = bcrypt.generate_password_hash('nikolaev').decode('utf-8')
    
    db.session.commit()