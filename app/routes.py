from flask import render_template, flash, redirect, url_for, request, session
from app import app, db
from app.forms import LoginForm, RegistrationForm, VerificationForm, AddMusic
from flask_login import current_user, login_user, logout_user, login_required
from app.models import *
import sqlalchemy as sa
from urllib.parse import urlsplit
from app.mail_send_code import generate_verification_code, send_verification_email
from datetime import datetime, timedelta
from config import Config
from sqlite3 import IntegrityError
import os
import uuid

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': 'Miguel'}
    posts = [
    {
        'author': {'username': 'John'},
        'body': 'Beautiful day in Portland!'
    },
    {
        'author': {'username': 'Susan'},
        'body': 'The Avengers movie was so cool!'
    }
    ]
    return render_template('index.html', title='Home', posts=posts)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
        sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        
        # Проверка, не существует ли уже такой пользователь в основной таблице
        existing_user = db.session.scalar(
            sa.select(User).where((User.username == form.username.data) | (User.email == form.email.data))
        )
        if existing_user:
            flash('Пользователь с таким именем или email уже существует.')
            return render_template('register.html', title='Register', form=form)
        
        # Проверка, нет ли уже в ожидании пользователь с такими данными
        pending_exists = db.session.scalar(
            sa.select(PendingUser).where(
                (PendingUser.username == form.username.data) | (PendingUser.email == form.email.data)
            )
        )
        if pending_exists:
            flash('Регистрация с этими данными уже начата. Проверьте почту или подождите.')
            return render_template('register.html', title='Register', form=form)
        
        pending_user = PendingUser(
            username=form.username.data, 
            email=form.email.data,
            password_hash=None  
        )
        
        # Хэшируем пароль
        pending_user.set_password(form.password.data) 
        
        verification_code = generate_verification_code()
        times = datetime.utcnow() + timedelta(minutes=Config.CODE_EXPIRY_MINUTES)
        
        pending_user.verification_code = verification_code
        pending_user.code_expires_at = times
        
        try:
            db.session.add(pending_user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('Ошибка: пользователь с таким именем или email уже существует.')
            return render_template('register.html', title='Register', form=form)
        
        session['pending_user_id'] = pending_user.id
        
        # Отправляем email
        if send_verification_email(pending_user.email, pending_user.verification_code):
            flash(f'Код подтверждения отправлен на {pending_user.email}')
        else:
            flash('Ошибка отправки email. Попробуйте позже.')
            db.session.delete(pending_user)
            db.session.commit()
            return render_template('register.html', title='Register', form=form)
        
        return redirect(url_for('verify'))
    
    return render_template('register.html', title='Register', form=form)
@app.route('/verify', methods=["GET", "POST"])
def verify():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Если зашли на страницу без регистрации
    pending_user_id = session.get('pending_user_id')
    if not pending_user_id:
        flash('Сначала зарегистрируйтесь.')
        return redirect(url_for('register'))
    
    form = VerificationForm()
    if form.validate_on_submit():
        pending_user = db.session.get(PendingUser, pending_user_id)
        
        if pending_user is None:
            flash('Данные не найдены. Зарегистрируйтесь заново.')
            session.pop('pending_user_id', None)
            return redirect(url_for('register'))
        
        #Проверка кода
        if form.code.data != str(pending_user.verification_code):
            flash('Неверный код подтверждения.')
            return render_template('verify.html', title='Verify', form=form)
        
        #Проверка срока действия введенного кода
        if datetime.utcnow() > pending_user.code_expires_at:
            flash('Код истёк. Зарегистрируйтесь заново.')
            db.session.delete(pending_user)
            db.session.commit()
            session.pop('pending_user_id', None)
            return redirect(url_for('register'))
        
        #Создаём пользователя
        user = User(username=pending_user.username, email=pending_user.email)
        user.password_hash = pending_user.password_hash
        
        db.session.add(user)
        db.session.delete(pending_user)
        db.session.commit()
        
        session.pop('pending_user_id', None)
        flash('Поздравляем! Вы успешно зарегистрированы. Теперь войдите.')
        return redirect(url_for('login'))
    
    return render_template('verify.html', title='Verify', form=form)

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    form = AddMusic()
    if form.validate_on_submit():
        files = form.file.data

        #Получаем оригинальное расширение файла
        ext = files.filename.rsplit(".", 1)[1].lower()
        #Уникальное имя файла
        unique_name = uuid.uuid4().hex + '.' + ext
        #Полный путь, куда будем сохранять файд
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        
        files.save(filepath)

        track = Track(
            title = form.title.data,
            artist = form.artist.data,
            filename = unique_name,
            user_id = current_user.id
        )

        db.session.add(track)
        db.session.commit()

        return redirect(url_for('upload'))
    return render_template('upload.html', title="Save", form=form)
