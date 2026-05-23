import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import random
import os
from config import Config



def generate_verification_code():
    return random.randint(100_000, 999_999)


def create_verification_message(recipient_email, code):
    message_text = f"""Здравствуйте!

Вы зарегистрировались в Music_Player. 
Ваш код подтверждения: {code}

Код действителен {Config.CODE_EXPIRY_MINUTES} минут. 

Если вы не запрашивали код, пожалуйста, проигнорируйте данное письмо.
Спасибо,
Команда {Config.SENDER_NAME}
"""

    msg = MIMEText(message_text, 'plain', 'utf-8')
    msg['From'] = f"{Config.SENDER_NAME} <{Config.LOGIN}>"
    msg['To'] = recipient_email
    msg['Subject'] = "Код подтверждения"
    msg['X-Priority'] = '1'
    msg['Importance'] = 'high'
    
    return msg

#Отправка письма
def send_verification_email(recipient_email, code):
    if not recipient_email or '@' not in recipient_email:
        raise ValueError("Некорректный email адрес")
    
    msg = create_verification_message(recipient_email, code)
    
    try:
        with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
            #Шифрование          
            server.starttls()
            #Авторизация
            server.login(Config.LOGIN, Config.PASSWORD)
            #Отправка письма
            server.sendmail(Config.LOGIN, recipient_email, msg.as_string())
        
        print(f"Письмо с кодом отправлено на {recipient_email}")
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
