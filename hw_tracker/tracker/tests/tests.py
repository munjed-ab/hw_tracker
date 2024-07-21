# tracker/tests/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Course, Homework
from ..tasks import move_deez, send_track_email
from datetime import datetime, timedelta
from unittest.mock import patch

class CeleryTaskTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.course = Course.objects.create(user=self.user, name='Test Course')
        self.homework1 = Homework.objects.create(
            course=self.course,
            name='Homework 1',
            start_date=datetime.now().date(),  # Temporary start_date
            due_date=datetime(year=2024, month=7, day=1).date(),
            days_left=10
        )
        self.homework2 = Homework.objects.create(
            course=self.course,
            name='Homework 2',
            start_date=datetime.now().date(),  # Temporary start_date
            due_date=datetime(year=2024, month=6, day=27).date(),
            days_left=5
        )
        # Add a temporary start_date to avoid NoneType error during the test
        self.homework3 = Homework.objects.create(
            course=self.course,
            name='Homework 3',
            due_date=datetime(year=2024, month=6, day=27).date(),
            start_date=datetime.now().date(),  # Temporary start_date
            days_left=None
        )

    def test_move_deez_task(self):
        # Run the task
        move_deez()

        # Refresh from database
        self.homework1.refresh_from_db()
        self.homework2.refresh_from_db()
        self.homework3.refresh_from_db()

        # Check if days_left has been decremented by 1
        self.assertEqual(self.homework1.days_left, 9)
        self.assertEqual(self.homework2.days_left, 4)
        self.assertEqual(self.homework3.days_left, (self.homework3.due_date - self.homework3.start_date).days - 1)

    # @patch('tracker.tasks.send_track_email')
    # def test_send_track_email_task(self, mock_send_email):
    #     # Run the task
    #     send_track_email()
    #
    #     # Check that the send email task was called
    #     self.assertTrue(mock_send_email.called)
