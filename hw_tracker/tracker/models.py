from datetime import datetime

from django.db import models
from django.contrib.auth.models import User


#helper function
def calc_time_left(start_date, due_date):
    due_date = datetime.strptime(due_date, '%Y-%m-%d')

    difference = due_date - start_date
    days = difference.days
    hours = difference.seconds // 3600
    return f"{days} days, {hours} hours left"

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
    time_left = models.CharField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.days_left is None:
            self.days_left = (self.due_date - datetime.today().date()).days
        self.time_left = calc_time_left(datetime.now(), datetime.strftime(self.due_date, r"%Y-%m-%d"))
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.course.name

    class Meta:
        ordering = ["-updated", "-created"]