from django.core.mail import send_mail
from django.conf import settings

from django_core.celery import app


@app.task
def send_message(mail_subject: str, mail_content: str) -> None:
    send_mail(
        subject=mail_subject,
        message=mail_content,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=settings.EMAIL_RECIPIENTS,
    )
