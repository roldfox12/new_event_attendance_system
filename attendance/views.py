from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import AttendanceForm, StudentRegistrationForm
from .models import Event, Attendance, Student, SBOOfficer
from django.utils import timezone

def sbo_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome, {user.username} from {user.college.name}!")
            return redirect('attendance_form')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'attendance/login.html')

def sbo_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('sbo_login')

@login_required(login_url='sbo_login')
def attendance_form(request):
    officer = request.user
    events = Event.objects.filter(college=officer.college)
    form = AttendanceForm(event_queryset=events)

    if request.method == 'POST':
        form = AttendanceForm(request.POST, event_queryset=events)
        if form.is_valid():
            id_number = form.cleaned_data['id_number']
            event = form.cleaned_data['event']
            action = form.cleaned_data['action']

            try:
                student = Student.objects.get(id_number=id_number, college=officer.college)
            except Student.DoesNotExist:
                messages.error(request, "Student not found in your college or not registered.")
                return redirect('attendance_form')

            try:
                existing_attendance = Attendance.objects.get(student=student, event=event)
            except Attendance.DoesNotExist:
                existing_attendance = None

            if action == 'am_sign_in':
                if existing_attendance:
                    if existing_attendance.am_sign_in_time and existing_attendance.am_sign_out_time:
                        messages.error(request, f"{student.name} has already signed in and out for AM session.")
                        return redirect('attendance_form')
                    elif existing_attendance.am_sign_in_time:
                        messages.warning(request, f"{student.name} is already signed in for AM.")
                        return redirect('attendance_form')
                    else:
                        existing_attendance.am_sign_in_time = timezone.now()
                        existing_attendance.save()
                else:
                    existing_attendance = Attendance.objects.create(
                        student=student,
                        event=event,
                        am_sign_in_time=timezone.now()
                    )
                messages.success(request, f"{student.name} signed in for AM successfully!")

            elif action == 'am_sign_out':
                if not existing_attendance:
                    messages.error(request, "No AM sign-in record found for this student and event.")
                    return redirect('attendance_form')
                elif existing_attendance.am_sign_out_time:
                    messages.warning(request, f"{student.name} has already signed out for AM.")
                    return redirect('attendance_form')
                else:
                    existing_attendance.am_sign_out_time = timezone.now()
                    existing_attendance.save()
                    messages.success(request, f"{student.name} signed out for AM successfully!")

            elif action == 'pm_sign_in':
                if existing_attendance:
                    if existing_attendance.pm_sign_in_time and existing_attendance.pm_sign_out_time:
                        messages.error(request, f"{student.name} has already signed in and out for PM session.")
                        return redirect('attendance_form')
                    elif existing_attendance.pm_sign_in_time:
                        messages.warning(request, f"{student.name} is already signed in for PM.")
                        return redirect('attendance_form')
                    else:
                        existing_attendance.pm_sign_in_time = timezone.now()
                        existing_attendance.save()
                else:
                    existing_attendance = Attendance.objects.create(
                        student=student,
                        event=event,
                        pm_sign_in_time=timezone.now()
                    )
                messages.success(request, f"{student.name} signed in for PM successfully!")

            elif action == 'pm_sign_out':
                if not existing_attendance:
                    messages.error(request, "No PM sign-in record found for this student and event.")
                    return redirect('attendance_form')
                elif existing_attendance.pm_sign_out_time:
                    messages.warning(request, f"{student.name} has already signed out for PM.")
                    return redirect('attendance_form')
                else:
                    existing_attendance.pm_sign_out_time = timezone.now()
                    existing_attendance.save()
                    messages.success(request, f"{student.name} signed out for PM successfully!")

    return render(request, 'attendance/attendance_form.html', {'form': form})

def student_registration(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Student registered successfully!")
            return redirect('attendance_form')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = StudentRegistrationForm()
    return render(request, 'attendance/student_registration.html', {'form': form})

