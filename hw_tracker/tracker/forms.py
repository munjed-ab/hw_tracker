from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User

class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','first_name','last_name', 'email', 'password1', 'password2']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].help_text = "You will get emails to notify you about the homeworks timeline"


from .models import Course, Homework
from datetime import datetime

class AddCourseForm(forms.Form):
    course_name = forms.CharField(max_length=255, required=True)
    homework_name = forms.CharField(max_length=255, required=False)
    due_date = forms.DateField(required=True)
    start_date = forms.DateField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        if not start_date:
            cleaned_data["start_date"] = datetime.today().date()
        return cleaned_data
