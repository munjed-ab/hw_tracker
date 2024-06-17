from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('signup/', views.signup, name='signup'),
    path('add_course/', views.add_course, name='add_course'),
    path('course/edit/<int:course_id>', views.edit_course, name='edit_course'),
    path('course/delete/<int:course_id>/', views.delete_course, name='delete_course'),
    path('fetch-hws/', views.fetch_hws, name='fetch_hws'),
]
