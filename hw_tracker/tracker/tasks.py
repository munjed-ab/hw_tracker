from celery import shared_task
from .models import Homework
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=2)
def log(self):
    try:
        homeworks = Homework.objects.all()
        print(f"Number of homeworks: {homeworks.count()}")
        for homework in homeworks:
            homework.days_left -= 1
            homework.save()
            print(f"Updated homework {homework.name} to {homework.days_left} days left")
    except Exception as exc:
        logger.error(f"Task failed: {exc}")
        raise self.retry(exc=exc)