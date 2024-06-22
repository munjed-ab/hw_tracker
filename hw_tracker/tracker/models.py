from datetime import date, datetime

from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    url = models.URLField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["-updated", "-created"]

class Homework(models.Model):
    course = models.ForeignKey(Course, related_name='homeworks', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True)
    url = models.URLField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    due_date = models.DateField()
    days_left = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.days_left is None:
            self.days_left = (self.due_date - datetime.today().date()).days
        super().save(*args, **kwargs)

    def __str__(self):
        return self.course.name

    class Meta:
        ordering = ["-updated", "-created"]