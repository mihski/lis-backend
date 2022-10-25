from django.core.mail import send_mail
from django.conf import settings

from django_core.celery import app
from lessons.models import EmailTypes


@app.task
def send_message(mail_subject: str, mail_content: str, mail_type: str) -> None:
    recipient_list = (
        settings.EMAIL_TECH if mail_type == EmailTypes.TECH
        else settings.EMAIL_RECIPIENTS
    )

    send_mail(
        subject=mail_subject,
        message=mail_content,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=recipient_list,
    )
