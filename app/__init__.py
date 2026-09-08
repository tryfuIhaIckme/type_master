import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
migrate = Migrate()


def create_app(config_class=None):
    app = Flask(__name__)

    if config_class:
        app.config.from_object(config_class)
    else:
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-key-replace-in-production'
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
            f'sqlite:///{os.path.join(os.path.dirname(os.path.dirname(__file__)), "instance", "site.db")}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Init extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)

    # Safe database setup
    with app.app_context():
        try:
            db.create_all()
            _ensure_admin()
        except Exception as e:
            print(f"Database setup error: {e}")
            db.session.rollback()

    return app


def _ensure_admin():
    """Создаёт админа по умолчанию, если его нет."""
    from app.models import User

    # Сбрасываем флаг админа у всех, кроме nikolaev
    User.query.filter(User.username != 'nikolaev').update({User.is_admin: False})

    admin = User.query.filter(
        (User.username == 'nikolaev') |
        (User.email == 'admin@typemaster.com')
    ).first()

    if not admin:
        hashed_password = bcrypt.generate_password_hash('nikolaev').decode('utf-8')
        admin = User(username='nikolaev', email='admin@typemaster.com',
                     password_hash=hashed_password, is_admin=True)
        db.session.add(admin)
    else:
        admin.username = 'nikolaev'
        admin.email = 'admin@typemaster.com'
        admin.is_admin = True
        admin.password_hash = bcrypt.generate_password_hash('nikolaev').decode('utf-8')

    db.session.commit()
