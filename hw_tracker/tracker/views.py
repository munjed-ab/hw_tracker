from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.template.loader import render_to_string

from .forms import UserForm, AddCourseForm, UpdateUserForm
from .models import Course, Homework
from .scrap import *
from datetime import datetime


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("dashboard")
    else:
        form = AuthenticationForm()
    return render(request, 'tracker/login.html', {'form': form})


def signup(request):
    form = UserForm()
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['password1'] == form.cleaned_data['password2']:
                user = form.save(commit=False)
                user.username = user.username.lower()
                user.save()
                messages.success(request, "User has been created successfully.")
                return redirect('login')
            else:
                messages.error(request, "Passwords are different, please check again.")
        else:
            messages.error(request, "Invalid inputs, please check again!")
    context = {"form": form}
    return render(request, "tracker/signup.html", context)


@login_required
def logout_view(request):
    if not request.user.is_authenticated:
        return redirect("login")
    logout(request)
    return redirect("login")


from datetime import datetime, date


@login_required
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("login")

    course_data = get_courses_cards(request.user)

    return render(request, 'tracker/dashboard.html', {'course_data': course_data})


@login_required
def refresh_data(request):
    if not request.user.is_authenticated:
        return redirect("login")
    courses = Course.objects.filter(user=request.user.id)
    for course in courses:
        homework = Homework.objects.get(course=course)
        homework.save()
    
    return redirect("dashboard")


@login_required
def update_user_profile(request):
    if request.method == 'POST':
        form = UpdateUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('dashboard')
    else:
        form = UpdateUserForm(instance=request.user)

    return render(request, 'tracker/update_user.html', {'form': form})

def get_courses_cards(user):
    courses = Course.objects.filter(user=user)
    course_data = []
    for course in courses:
        homeworks = Homework.objects.filter(course=course)
        homework_data = []

        for homework in homeworks:
            if homework.start_date and homework.due_date:
                
                difference1 = datetime.strptime(homework.due_date.strftime(r"%d-%m-%Y"), r"%d-%m-%Y") - datetime.now()
                days_left = ((difference1.seconds // 3600)/24) + difference1.days

                difference2 = (datetime.now() - datetime.strptime(homework.start_date.strftime(r"%d-%m-%Y"), r"%d-%m-%Y"))
                days_passed = ((difference2.seconds // 3600)/24) + difference2.days

                total_duration = float(days_left) + float(days_passed)
                progress_percentage = (days_passed / total_duration) * 100 if total_duration != 0 else 0

            else:
                progress_percentage = 0
                days_left = 0

            homework_data.append({
                'homework': homework,
                'progress_percentage': progress_percentage,
                'days_left': days_left
            })

        course_data.append({
            'course': course,
            'homeworks': homework_data
        })
    return course_data

def calc_time_left(start_date, due_date):
    due_date = datetime.strptime(due_date, r'%Y-%m-%d')

    difference = due_date - start_date
    days = difference.days
    hours = difference.seconds // 3600
    return f"{days} days, {hours} hours left"

@login_required
def add_course(request):
    if request.method == 'POST':
        form = AddCourseForm(request.POST)
        if form.is_valid():
            course_name = form.cleaned_data['course_name']
            homework_name = form.cleaned_data['homework_name']
            due_date = form.cleaned_data['due_date']
            start_date = form.cleaned_data['start_date']

            course = Course.objects.create(user=request.user, name=course_name)
            homework = Homework.objects.create(
                course=course,
                name=homework_name,
                start_date=start_date,
                due_date=due_date,
                url="#"
            )

            # Calculate days left and total duration
            days_left = (due_date - datetime.today().date()).days
            days_passed = (datetime.today().date() - start_date).days
            total_duration = days_left + days_passed
            progress_percentage = (days_passed / total_duration) * 100 if total_duration != 0 else 0

            homework.days_left = days_left
            homework.time_left = calc_time_left(datetime.now(), str(due_date))
            homework.save()

            course_data = {
                'course': course,
                'homework': homework,
                'progress_percentage': progress_percentage,
                'days_left': days_left
            }
            course_html = render_to_string('tracker/course_item.html', {'course_data': course_data})
            return HttpResponse(course_html)
        messages.error(request, "Invalid Inputs, please check again.")
    messages.error(request, "Access Denied.")
    return HttpResponseBadRequest("Invalid form data")


@login_required
def edit_course(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
        homework = Homework.objects.get(course=course_id)

        if request.method == "POST":
            course_name = request.POST['course_name']
            homework_name = request.POST['homework_name']
            due_date = request.POST['due_date']
            start_date = request.POST['start_date']

            start_date = datetime.strptime(start_date, r'%Y-%m-%d').date()

            due_date = datetime.strptime(due_date, r'%Y-%m-%d').date()

            course.name = course_name
            course.save()

            homework.name = homework_name
            homework.start_date = start_date if start_date else datetime.today().date()
            homework.due_date = due_date

            days_left = (due_date - datetime.today().date()).days
            homework.days_left = days_left
            homework.save()
            messages.success(request, f"{course.name} was updated successfully.")
            return redirect("dashboard")
        else:
            return render(request, "tracker/edit_course.html", context={"course": course, "homework": homework})
    except:
        messages.error(request, "Invalid Inputs, please check again.")
        return redirect("dashboard")

@login_required
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, user=request.user)
    course_name = course.name
    if request.method == 'POST':
        course.delete()
        messages.success(request, f"{course_name} was deleted successfully.")
        return redirect('dashboard')
    return render(request, 'tracker/delete_course.html', {'course': course})



from django.views.decorators.csrf import csrf_exempt

@login_required
@csrf_exempt
def fetch_hws(request):
    if request.method == 'POST':
        svu_id = request.POST.get('svu-id')
        svu_pass = request.POST.get('svu-pass')
        user = request.user

        # Use Selenium to scrape data
        scraped_data = scrap_deez(svu_pass, svu_id)

        if 'Timeout Error' in scraped_data:
            messages.error(request, "Sorry I couldn't fetch your data, check your connection")
            return redirect("dashboard")
        if not scraped_data:
            messages.error(request, "Sorry I couldn't fetch your data, something went wrong")
            return redirect("dashboard")
        if 'Connection Aborted' in scraped_data:
            messages.error(request, "Sorry I couldn't fetch your data, check your password")
            return redirect("dashboard")

        # Save scraped data to the database
        # count = len(scraped_data['courses'])
        for course in scraped_data['courses']:
            course_obj, created = Course.objects.get_or_create(user=user, name=course['name'], url=course['url'])
            for hw in course['homeworks']:
                # Check if homework with the same name already exists for the course
                existing_hw = Homework.objects.filter(course=course_obj).first()
                if existing_hw:
                    # Update existing homework
                    existing_hw.url = hw['url'] if hw['url'] else "#"
                    existing_hw.name = hw['name']
                    existing_hw.start_date = datetime.strptime(hw['start_date'], '%c')
                    existing_hw.due_date = datetime.strptime(hw['end_date'], '%c')
                    existing_hw.days_left = int(hw['days_left']) if hw['days_left'].isdigit() else 0
                    existing_hw.save()
                else:
                    # Create new homework
                    Homework.objects.create(
                        course=course_obj,
                        name=hw['name'],
                        url=hw['url'] if hw['url'] else "#",
                        start_date=datetime.strptime(hw['start_date'], '%c'),
                        due_date=datetime.strptime(hw['end_date'], '%c'),
                        days_left=int(hw['days_left']) if hw['days_left'].isdigit() else 0
                    )

        # Get the updated course list
        course_data = get_courses_cards(user)

        # Render the updated course list
        html = render_to_string('tracker/course_list.html', {'course_data': course_data}, request=request)
        return HttpResponse(html)
    return HttpResponseBadRequest('Invalid request')
