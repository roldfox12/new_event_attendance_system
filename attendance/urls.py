# attendance/urls.py
from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    path('', lambda request: redirect('sbo_login'), name='home'),
    path('superuser/dashboard/', views.superuser_dashboard, name='superuser_dashboard'),
    path('sbo/login/', views.sbo_login, name='sbo_login'),
    path('sbo/logout/', views.sbo_logout, name='sbo_logout'),
    path('attendance/form/', views.attendance_form, name='attendance_form'),
    path('attendance/print/', views.print_attendance, name='print_attendance'),
    path('student/register/', views.student_registration, name='student_registration'),
    path('event/delete/<int:event_id>/', views.delete_event, name='delete_event'),
    path('officer/delete/<int:officer_id>/', views.delete_officer, name='delete_officer'),
    path('student/delete/<int:student_id>/', views.delete_student, name='delete_student'),
]