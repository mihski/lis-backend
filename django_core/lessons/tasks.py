from django.core.mail import send_mail
from django.conf import settings

from django_core.celery import app
from helpers.google_sheets import GoogleSheetsConnection, GoogleSheetsAdapter

google_sheet_connection = GoogleSheetsConnection().get_connection()


@app.task
def send_message(mail_subject: str, mail_content: str, mail_type: str) -> None:
    from lessons.models import EmailTypes

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


@app.task
def upload_profile_course_finished_gsheets(profile_finished_course_data: dict) -> None:
    GoogleSheetsAdapter(google_sheet_connection).update_profile_course_finished(profile_finished_course_data)
