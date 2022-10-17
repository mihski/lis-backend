from typing import Literal, Tuple

from django.db.models.signals import post_save
from django.dispatch import receiver

from lessons.models import Question, Review
from lessons.tasks import send_message


def prepare_data(*, instance: Review | Question, feedback_type: Literal["review", "question"]) -> Tuple[str, str]:
    course_name = instance.course.name
    user = instance.user
    text = instance.text

    if feedback_type == "question":
        mail_subject = f"Вопрос по курсу \"{course_name}\""
        mail_message = f"Новый вопрос от студента <{user.first_name} {user.last_name}>:\n"
    else:
        mail_subject = f"Отзыв по курсу \"{course_name}\""
        mail_message = f"Новый отзыв от студента <{user.first_name} {user.last_name}>:\n"

    mail_message += (
        f"{text}\n"
        f"Почта студента: {user.email}"
    )

    return mail_subject, mail_message


@receiver(post_save, sender=Review)
def send_email_after_review_created(sender, instance: Review, **kwargs: dict) -> None:
    subject, msg = prepare_data(instance=instance, feedback_type="review")
    send_message.delay(subject, msg)


@receiver(post_save, sender=Question)
def send_email_after_question_created(sender, instance: Question, **kwargs: dict) -> None:
    subject, msg = prepare_data(instance=instance, feedback_type="question")
    send_message.delay(subject, msg)
