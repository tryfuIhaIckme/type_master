import os
from app import app

app.config.from_object('config.Config')


def create_app():
    """Фабрика приложения для поддержки тестов и разных окружений."""
    return app


if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    app.run(debug=debug_mode, host='0.0.0.0')
