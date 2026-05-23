from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-key-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
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
    
    # Сбрасываем флаг админа у всех, кроме adminka
    models.User.query.filter(models.User.username != 'adminka').update({models.User.is_admin: False})
    
    admin = models.User.query.filter_by(username='adminka').first()
    if not admin:
        hashed_password = bcrypt.generate_password_hash('123').decode('utf-8')
        admin = models.User(username='adminka', email='admin@typemaster.com', 
                            password_hash=hashed_password, is_admin=True)
        db.session.add(admin)
    else:
        admin.is_admin = True
        admin.password_hash = bcrypt.generate_password_hash('123').decode('utf-8')
    
    db.session.commit()