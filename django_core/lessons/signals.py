from typing import Literal, Tuple

from django.db.models.signals import post_save
from django.dispatch import receiver

from lessons.models import Question, Review, EmailTypes
from lessons.tasks import send_message


def prepare_data(*, instance: Review | Question, feedback_type: Literal["review", "question"]) -> Tuple[str, str, str]:
    course_name = instance.course.name
    current_user = instance.user
    text = instance.text
    mail_type = instance.mail_type if isinstance(instance, Review) else EmailTypes.CONTENT

    if feedback_type == "question":
        mail_subject = f"Вопрос по курсу \"{course_name}\""
        mail_message = f"Новый вопрос от студента <{current_user.first_name} {current_user.last_name}>:\n"
    else:
        mail_subject = f"Отзыв по курсу \"{course_name}\""
        mail_message = f"Новый отзыв от студента <{current_user.first_name} {current_user.last_name}>:\n"

    mail_message += (
        f"{text}\n"
        f"Номер студента: {current_user.username}"
        f"Почта студента: {current_user.email}"
    )

    return mail_subject, mail_message, mail_type


@receiver(post_save, sender=Review)
def send_email_after_review_created(sender, instance: Review, **kwargs: dict) -> None:
    subject, msg, mail_type = prepare_data(instance=instance, feedback_type="review")
    send_message.delay(subject, msg, mail_type)


@receiver(post_save, sender=Question)
def send_email_after_question_created(sender, instance: Question, **kwargs: dict) -> None:
    subject, msg, mail_type = prepare_data(instance=instance, feedback_type="question")
    send_message.delay(subject, msg, mail_type)
