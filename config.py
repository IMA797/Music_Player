import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()


class Config:
    # os.environ.get - читаем переменные окружения из системы
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Eeeee-body-light-weight-baby'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')

    SMTP_SERVER = os.environ.get('SMTP_SERVER') or 'smtp.mail.ru'
    SMTP_PORT = int(os.environ.get('SMTP_PORT') or 587)
    SMTP_LOGIN = os.environ.get('SMTP_LOGIN') or ''
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD') or ''
    SENDER_NAME = os.environ.get('SENDER_NAME') or 'Music_Player'
    CODE_EXPIRY_MINUTES = 5

    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')