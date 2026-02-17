from flask import render_template, url_for, flash, redirect, request, abort, Response
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, TextForm, UploadForm
from app.models import User, Text, TestSession, Result
from flask_login import login_user, current_user, logout_user, login_required
import json
from sqlalchemy import func
from io import StringIO
import csv

@app.route("/")
@app.route("/home")
def index():
    return render_template('index.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Аккаунт создан! Теперь вы можете войти.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Регистрация', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('index'))
        else:
            flash('Ошибка входа. Проверьте email и пароль', 'danger')
    return render_template('login.html', title='Вход', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/texts")
@login_required
def texts_list():
    texts = Text.query.all()
    return render_template('texts_list.html', texts=texts)

@app.route("/text/new", methods=['GET', 'POST'])
@login_required
def new_text():
    if not current_user.is_admin:
        abort(403)
    form = TextForm()
    if form.validate_on_submit():
        text = Text(title=form.title.data, content=form.content.data, 
                    language=form.language.data, difficulty=form.difficulty.data)
        db.session.add(text)
        db.session.commit()
        flash('Текст добавлен!', 'success')
        return redirect(url_for('texts_list'))
    return render_template('edit_text.html', title='Новый текст', form=form)

@app.route("/text/upload", methods=['GET', 'POST'])
@login_required
def upload_file():
    if not current_user.is_admin:
        abort(403)
    form = UploadForm()
    if form.validate_on_submit():
        if form.file.data:
            file_content = form.file.data.read().decode("utf-8")
            text = Text(title=form.file.data.filename, content=file_content)
            db.session.add(text)
            db.session.commit()
            flash('Файл загружен!', 'success')
            return redirect(url_for('texts_list'))
    return render_template('upload.html', form=form)

@app.route("/test/<int:text_id>")
@login_required
def typing_test(text_id):
    text = Text.query.get_or_404(text_id)
    return render_template('test.html', title='Тест печати', text=text)

@app.route("/save_result", methods=['POST'])
@login_required
def save_result():
    data = request.get_json()
    # 1. Создаем сессию теста
    session = TestSession(user_id=current_user.id, text_id=data['text_id'])
    db.session.add(session)
    db.session.flush() # Получаем ID сессии до фиксации в БД
    
    # 2. Создаем результат
    result = Result(
        session_id=session.id,
        wpm=data['wpm'],
        accuracy=data['accuracy'],
        errors_count=data['errors']
    )
    db.session.add(result)
    db.session.commit()
    return json.dumps({'status': 'success'}), 200

@app.route("/profile")
@login_required
def profile():
    user_results = Result.query.join(TestSession).filter(TestSession.user_id == current_user.id).all()
    
    stats = db.session.query(
        func.avg(Result.wpm).label('avg_wpm'),
        func.max(Result.wpm).label('best_wpm'),
        func.count(Result.id).label('total_tests')
    ).join(TestSession).filter(TestSession.user_id == current_user.id).first()

    return render_template('profile.html', results=user_results, stats=stats)

@app.route("/export_results")
@login_required
def export_results():
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Дата', 'WPM', 'Точность %', 'Ошибки']) # Заголовки
    
    results = Result.query.join(TestSession).filter(TestSession.user_id == current_user.id).all()
    for r in results:
        cw.writerow([r.created_at.strftime('%Y-%m-%d %H:%M'), r.wpm, r.accuracy, r.errors_count])
    
    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=my_results.csv"}
    )