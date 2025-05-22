from django.urls import path
from . import views

urlpatterns = [
    path('', views.sbo_login, name='sbo_login'),
    path('logout/', views.sbo_logout, name='sbo_logout'),
    path('attendance/', views.attendance_form, name='attendance_form'),
    path('register/', views.student_registration, name='student_registration'),
]