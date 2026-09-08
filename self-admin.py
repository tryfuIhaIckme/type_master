"""Скрипт для назначения прав админа пользователю."""
from run import create_app
from app import db
from app.models import User

app = create_app()

with app.app_context():
    username = input("Введите имя пользователя: ").strip()
    u = User.query.filter_by(username=username).first()
    if u:
        u.is_admin = True
        db.session.commit()
        print(f"Пользователь {u.username} теперь АДМИН!")
    else:
        print("Пользователь не найден!")
