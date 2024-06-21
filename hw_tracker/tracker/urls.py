from django.urls import path
from . import views
from django.contrib.auth import views as views_auth

from .forms import CustomPasswordResetForm

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('signup/', views.signup, name='signup'),
    path('add_course/', views.add_course, name='add_course'),
    path('course/edit/<int:course_id>', views.edit_course, name='edit_course'),
    path('course/delete/<int:course_id>/', views.delete_course, name='delete_course'),
    path('fetch-hws/', views.fetch_hws, name='fetch_hws'),
    path('update-profile/', views.update_user_profile, name='update_profile'),

    # AUTH
    path("password_reset/",
         views_auth.PasswordResetView.as_view(
             template_name="tracker/auth/password_reset.html",
             email_template_name='tracker/auth/password_reset_email.html',
             form_class=CustomPasswordResetForm),
         name="password_reset"),
    path("password_reset_done/",
         views_auth.PasswordResetDoneView.as_view(template_name="tracker/auth/password_reset_sent.html"),
         name="password_reset_done"),
    path("password_reset_confirm/<uidb64>/<token>/",
         views_auth.PasswordResetConfirmView.as_view(template_name="tracker/auth/password_reset_confirm.html"),
         name="password_reset_confirm"),
    path("password_reset_complete",
         views_auth.PasswordResetCompleteView.as_view(
             template_name="tracker/auth/password_reset_complete.html"),
         name="password_reset_complete"),
]
