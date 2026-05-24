import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate

app = Flask(__name__)

# Настройка путей для PythonAnywhere
basedir = os.path.abspath(os.path.dirname(__file__))
# Папка instance должна существовать для SQLite
instance_path = os.path.join(os.path.dirname(basedir), 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-123-replace-this-in-prod')
# Явный абсолютный путь к базе данных
db_path = os.path.join(instance_path, 'site.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f'sqlite:///{db_path}')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
migrate = Migrate(app, db)

from app import routes, models

# Безопасное создание таблиц и админа
def setup_database():
    with app.app_context():
        try:
            db.create_all()
            
            # Сбрасываем флаг админа у всех, кроме nikolaev
            models.User.query.filter(models.User.username != 'nikolaev').update({models.User.is_admin: False})
            
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
                admin.username = 'nikolaev'
                admin.email = 'admin@typemaster.com'
                admin.is_admin = True
                admin.password_hash = bcrypt.generate_password_hash('nikolaev').decode('utf-8')
            
            db.session.commit()
        except Exception as e:
            print(f"Database setup error: {e}")
            db.session.rollback()

setup_database()