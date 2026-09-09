"""Скрипт для создания админа."""
from app import app, db, bcrypt
from app.models import User

with app.app_context():
    # Удаляем старого админа если есть
    admin = User.query.filter_by(username='nikolaev').first()
    if admin:
        db.session.delete(admin)
        db.session.commit()
        print("Старый админ удалён")
    
    # Создаём нового
    admin = User(
        username='nikolaev',
        email='admin@typemaster.com',
        is_admin=True
    )
    hashed_pw = bcrypt.generate_password_hash('nikolaev').decode('utf-8')
    admin.password_hash = hashed_pw
    db.session.add(admin)
    db.session.commit()
    print(f"Админ nikolaev создан с паролем 'nikolaev'")
    print(f"Хеш: {hashed_pw}")
