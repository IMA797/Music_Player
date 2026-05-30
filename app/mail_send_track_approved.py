import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import random
import os
from config import Config

def approved_message(recipient_email):
    message_text = f"""Здравствуйте!
    Поздравляю, Ваш трек одобрен. 

    Если вы не отправляли трек, пожалуйста, проигнорируйте данное письмо. 
    Спасибо, 
    Команда {Config.SENDER_NAME}
    """

    msg = MIMEText(message_text, 'plain', 'utf-8')
    msg['From'] = f"{Config.SENDER_NAME} <{Config.SMTP_LOGIN}>"
    msg['To'] = recipient_email
    msg['Subject'] = "Результат добавления трека"
    msg['X-Priority'] = '1'
    msg['Importance'] = 'high'

    return msg 

def not_approved_message(recipient_email):
    message_text = f"""Здравствуйте!
    К сожалению, ваш трек модерацию не прошел. 

    Если вы не отправляли трек, пожалуйста, проигнорируйте данное письмо. 
    Спасибо, 
    Команда {Config.SENDER_NAME}
    """

    msg = MIMEText(message_text, 'plain', 'utf-8')
    msg['From'] = f"{Config.SENDER_NAME} <{Config.SMTP_LOGIN}>"
    msg['To'] = recipient_email
    msg['Subject'] = "Результат добавления трека"
    msg['X-Priority'] = '1'
    msg['Importance'] = 'high'

    return msg 

def send_track_approved_email(recipient_email):

    msg = approved_message(recipient_email)

    try:
        with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
            #Шифрование tls        
            server.starttls()
            #Авторизация
            server.login(Config.SMTP_LOGIN, Config.SMTP_PASSWORD)
            #Отправка письма
            server.sendmail(Config.SMTP_LOGIN, recipient_email, msg.as_string())
        
        print(f"Письмо с результатом добавления трека отправлено на {recipient_email}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("Ошибка аутентификации: проверьте логин и пароль приложения")
        return False
    except smtplib.SMTPException as e:
        print(f"SMTP ошибка при отправке: {e}")
        return False
    except Exception as e:
        print(f"Неожиданная ошибка при отправке письма: {e}")
        return False


def send_track_not_approved_email(recipient_email):

    msg = not_approved_message(recipient_email)

    try:
        with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
            #Шифрование tls        
            server.starttls()
            #Авторизация
            server.login(Config.SMTP_LOGIN, Config.SMTP_PASSWORD)
            #Отправка письма
            server.sendmail(Config.SMTP_LOGIN, recipient_email, msg.as_string())
        
        print(f"Письмо с результатом добавления трека отправлено на {recipient_email}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("Ошибка аутентификации: проверьте логин и пароль приложения")
        return False
    except smtplib.SMTPException as e:
        print(f"SMTP ошибка при отправке: {e}")
        return False
    except Exception as e:
        print(f"Неожиданная ошибка при отправке письма: {e}")
        return False