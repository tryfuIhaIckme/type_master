from app import app, db
from app.models import User

with app.app_context():
    u = User.query.filter_by(username='adminka').first()
    if u:
        u.is_admin = True
        db.session.commit()
        print(f"Пользователь {u.username} теперь АДМИН!")
    else:
        print("Пользователь не найден!")
