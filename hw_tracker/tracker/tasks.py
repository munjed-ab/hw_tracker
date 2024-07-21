from celery import shared_task
from django.db import transaction
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from .models import Homework
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=2)
def move_deez(self):
    try:
        with transaction.atomic():
            homeworks = Homework.objects.all()
            logger.info(f"Logger DB: Number of homeworks: {homeworks.count()}")
            for homework in homeworks:
                if homework.days_left > 0:
                    homework.days_left -= 1
                    homework.save()
                    logger.info(f"Logger DB: Updated homework {homework.name} to {homework.days_left} days left")
                logger.info(f"Logger DB: Homework {homework.name} has {homework.days_left} days left")
    except Exception as exc:
        logger.error(f"Logger DB: Task failed: {exc}")
        raise self.retry(exc=exc)

@shared_task(bind=True, max_retries=2)
def send_track_email(self):
    try:
        with transaction.atomic():
            homeworks = Homework.objects.all()
            for homework in homeworks:
                total_days = (homework.due_date - homework.start_date).days
                first_quarter = total_days // 4
                half = total_days // 2
                last_quarter = 3 * total_days // 4

                if homework.days_left in [first_quarter, half, last_quarter, 0]:
                    subject = f"Reminder: {homework.course.name} - {homework.name}"
                    message = f"""
                    Dear {homework.course.user.first_name},

                    This is a friendly reminder that your homework "{homework.name}" for the course "{homework.course.name}" has reached an important milestone.

                    Days left for this homework: {homework.days_left}

                    Please make sure to complete it on time.

                    Best regards,
                    Homework Tracker Team
                    """
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [homework.course.user.email],
                        fail_silently=False,
                    )
                    # msg = EmailMultiAlternatives(subject=subject, body=message, from_email=settings.DEFAULT_FROM_EMAIL, to=[homework.course.user.email])
                    # msg.send()
                    logger.info(f"Logger Email: Sent reminder email for {homework.name} to {homework.course.user.email}")

    except Exception as exc:
        logger.error(f"Logger Email: Task failed: {exc}")
        raise self.retry(exc=exc)
