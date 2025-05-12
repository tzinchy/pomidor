import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Union

from core.config import settings


class AuthEmailService:
    def _create_base_email_template(self, title: str, content: str) -> str:
        """Базовый шаблон для всех писем"""
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f3f4f6; height: 100%;">
                <div style="
                    max-width: 600px;
                    width: 100%;
                    margin: 20px auto;
                    background-color: #ffffff;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                    <h2 style="color: #1f2937; margin-top: 0;">{title}</h2>
                    <div style="font-size: 16px; color: #4b5563;">
                        {content}
                    </div>
                    <p style="font-size: 14px; color: #6b7280; margin-top: 30px;">
                        С уважением,<br>Ваша команда
                    </p>
                </div>
            </body>
        </html>
        """

    def create_password_reset_email(self, new_password: str) -> str:
        """HTML для письма с новым паролем"""
        title = "Ваш новый пароль"
        content = f"""
        <p>Добрый день!</p>
        <p>Ваш новый пароль:</p>
        <div style="
            margin: 20px 0;
            padding: 15px;
            background-color: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            font-size: 20px;
            font-weight: bold;
            color: #1f2937;
            text-align: center;">
            {new_password}
        </div>
        <p style="font-size: 14px; color: #6b7280;">
            Вы можете скопировать пароль, выделив его и нажав <b>Ctrl+C</b> (или <b>Cmd+C</b> на Mac).
        </p>
        """
        return self._create_base_email_template(title, content)

    def create_login_notification_email(self, first_name: str, last_name: str) -> str:
        """HTML для письма об успешном входе"""
        title = "Успешный вход в аккаунт"
        content = f"""
        <p>Добрый день, {first_name} {last_name}!</p>
        <p>Мы зафиксировали успешный вход в ваш аккаунт.</p>
        <p style="color: #ef4444; font-weight: 500;">
            Если это были не вы, пожалуйста, немедленно смените пароль и свяжитесь с поддержкой.
        </p>
        """
        return self._create_base_email_template(title, content)

    def create_password_update_confirmation(self, first_name: str) -> str:
        """HTML для письма об успешном изменении пароля"""
        title = "Пароль успешно изменен"
        content = f"""
        <p>Добрый день, {first_name}!</p>
        <div style="
            margin: 20px 0;
            padding: 15px;
            background-color: #f0fdf4;
            border: 1px solid #bbf7d0;
            border-radius: 8px;
            font-size: 16px;
            text-align: center;
            color: #166534;">
            Ваш пароль был успешно изменен
        </div>
        <p style="font-size: 14px; color: #4b5563;">
            Если это были не вы, пожалуйста, немедленно свяжитесь с поддержкой.
        </p>
        """
        return self._create_base_email_template(title, content)

    def send_email(self, recipients: Union[str, List[str]], subject: str, html_body: str) -> bool:
        """Общий метод для отправки email"""
        if isinstance(recipients, str):
            recipients = [recipients]

        msg = MIMEMultipart()
        msg['From'] =settings.email_settings.EMAIL_SENDER
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject
        msg.attach(MIMEText(html_body, 'html'))

        try:
            with smtplib.SMTP(settings.email_settings.EMAIL_SERVER, settings.email_settings.EMAIL_PORT) as server:
                server.starttls()
                server.login(settings.email_settings.EMAIL_LOGIN, settings.email_settings.EMAIL_PASSWORD)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Email sending failed: {str(e)}")
            return False

    def send_password_reset(self, email: str, new_password: str) -> bool:
        """Отправка письма с новым паролем"""
        html = self.create_password_reset_email(new_password)
        return self.send_email(email, "Ваш новый пароль", html)

    def send_login_notification(self, email: str, first_name: str, middle_name: str) -> bool:
        """Отправка уведомления о входе в аккаунт"""
        html = self.create_login_notification_email(first_name, middle_name)
        return self.send_email(email, "Успешный вход в аккаунт", html)

    def send_password_update_notification(self, email: str, first_name: str) -> bool:
        """Отправка уведомления об успешном изменении пароля"""
        html = self.create_password_update_confirmation(first_name)
        return self.send_email(email, "Пароль успешно изменен", html)