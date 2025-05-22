# attendance/views.py
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .forms import AttendanceForm, StudentRegistrationForm, EventForm, SBOOfficerForm, StudentForm
from .models import Event, Attendance, Student, SBOOfficer, College

# Set up logging
logger = logging.getLogger(__name__)

def sbo_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                logger.info(f"User {user.username} logged in successfully.")
                messages.success(request, f"Welcome, {user.username} from {user.college.name}!")
                if user.is_superuser:
                    return redirect('superuser_dashboard')
                return redirect('attendance_form')
            else:
                logger.warning(f"Failed login attempt for username: {username}")
                messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'attendance/login.html', {'form': form})

def sbo_logout(request):
    username = request.user.username if request.user.is_authenticated else "Anonymous"
    logout(request)
    logger.info(f"User {username} logged out.")
    messages.success(request, "You have been logged out.")
    return redirect('sbo_login')

@login_required(login_url='sbo_login')
def attendance_form(request):
    if request.user.is_superuser:
        return redirect('superuser_dashboard')

    officer = request.user
    events = Event.objects.filter(college=officer.college)
    # Remove students = Student.objects.filter(college=officer.college)
    form = AttendanceForm(
        request.POST or None,
        event_queryset=events  # Only pass event_queryset
    )
    selected_event = None

    if request.method == 'POST' and form.is_valid():
        id_number = form.cleaned_data['id_number']
        event = form.cleaned_data['event']
        action = form.cleaned_data['action']
        selected_event = event.name

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
            logger.info(f"AM sign-in recorded for {student.name} at event {event.name} by officer {officer.username}.")
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
            logger.info(f"AM sign-out recorded for {student.name} at event {event.name} by officer {officer.username}.")
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
            logger.info(f"PM sign-in recorded for {student.name} at event {event.name} by officer {officer.username}.")
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
            logger.info(f"PM sign-out recorded for {student.name} at event {event.name} by officer {officer.username}.")
            messages.success(request, f"{student.name} signed out for PM successfully!")

    attendance_logs = Attendance.objects.filter(event__college=officer.college).select_related('student', 'event').order_by('-created_at')

    return render(request, 'attendance/attendance_form.html', {
        'form': form,
        'attendance_logs': attendance_logs,
        'selected_event': selected_event,
        'events': events,
    })

@login_required(login_url='sbo_login')
def print_attendance(request):
    officer = request.user
    events = Event.objects.filter(college=officer.college)
    event_id = request.GET.get('event_id')
    event_name = None
    attendance_logs = []

    if event_id:
        event = get_object_or_404(Event, id=event_id, college=officer.college)
        event_name = event.name
        attendance_logs = Attendance.objects.filter(event=event).select_related('student').order_by('-created_at')

    return render(request, 'attendance/print_attendance.html', {
        'events': events,
        'event_name': event_name,
        'attendance_logs': attendance_logs,
    })

def student_registration(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save()
            logger.info(f"Student {student.name} registered successfully.")
            messages.success(request, "Student registered successfully!")
            return redirect('sbo_login')  # Redirect to login instead of attendance_form
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = StudentRegistrationForm()
    return render(request, 'attendance/student_registration.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def superuser_dashboard(request):
    event_form = EventForm(request.POST or None, prefix='event')
    officer_form = SBOOfficerForm(request.POST or None, prefix='officer')
    student_form = StudentForm(request.POST or None, request.FILES or None, prefix='student')

    if request.method == 'POST':
        if 'event_submit' in request.POST:
            if event_form.is_valid():
                event = event_form.save()
                logger.info(f"Event {event.name} created by superuser {request.user.username}.")
                messages.success(request, "Event created successfully!")
                return redirect('superuser_dashboard')
            else:
                messages.error(request, "Event form has errors. Please correct them.")

        elif 'event_edit' in request.POST:
            event_id = request.POST.get('event_id')
            event = get_object_or_404(Event, id=event_id)
            event_form = EventForm(request.POST, instance=event, prefix='event')
            if event_form.is_valid():
                event = event_form.save()
                logger.info(f"Event {event.name} updated by superuser {request.user.username}.")
                messages.success(request, "Event updated successfully!")
                return redirect('superuser_dashboard')
            else:
                messages.error(request, "Event edit form has errors. Please correct them.")

        elif 'officer_submit' in request.POST:
            if officer_form.is_valid():
                officer = officer_form.save()
                logger.info(f"SBO Officer {officer.username} added by superuser {request.user.username}.")
                messages.success(request, "SBO Officer added successfully!")
                return redirect('superuser_dashboard')
            else:
                messages.error(request, "Officer form has errors. Please correct them.")

        elif 'officer_edit' in request.POST:
            officer_id = request.POST.get('officer_id')
            officer = get_object_or_404(SBOOfficer, id=officer_id)
            officer_form = SBOOfficerForm(request.POST, instance=officer, prefix='officer')
            if officer_form.is_valid():
                officer = officer_form.save()
                logger.info(f"SBO Officer {officer.username} updated by superuser {request.user.username}.")
                messages.success(request, "SBO Officer updated successfully!")
                return redirect('superuser_dashboard')
            else:
                messages.error(request, "Officer edit form has errors. Please correct them.")

        elif 'student_submit' in request.POST:
            if student_form.is_valid():
                student = student_form.save()
                logger.info(f"Student {student.name} added by superuser {request.user.username}.")
                messages.success(request, "Student added successfully!")
                return redirect('superuser_dashboard')
            else:
                messages.error(request, "Student form has errors. Please correct them.")

        elif 'student_edit' in request.POST:
            student_id = request.POST.get('student_id')
            student = get_object_or_404(Student, id=student_id)
            student_form = StudentForm(request.POST, request.FILES, instance=student, prefix='student')
            if student_form.is_valid():
                student = student_form.save()
                logger.info(f"Student {student.name} updated by superuser {request.user.username}.")
                messages.success(request, "Student updated successfully!")
                return redirect('superuser_dashboard')
            else:
                messages.error(request, "Student edit form has errors. Please correct them.")

    events = Event.objects.all().select_related('college')
    officers = SBOOfficer.objects.all().select_related('college')
    students = Student.objects.all().select_related('college')
    attendance_logs = Attendance.objects.all().select_related('student', 'event').order_by('-created_at')

    return render(request, 'attendance/superuser_dashboard.html', {
        'event_form': event_form,
        'officer_form': officer_form,
        'student_form': student_form,
        'events': events,
        'officers': officers,
        'students': students,
        'attendance_logs': attendance_logs,
    })

@user_passes_test(lambda u: u.is_superuser)
def delete_event(request, event_id):
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        event_name = event.name
        event.delete()
        logger.info(f"Event {event_name} deleted by superuser {request.user.username}.")
        messages.success(request, "Event deleted successfully!")
    return redirect('superuser_dashboard')

@user_passes_test(lambda u: u.is_superuser)
def delete_officer(request, officer_id):
    if request.method == 'POST':
        officer = get_object_or_404(SBOOfficer, id=officer_id)
        officer_username = officer.username
        officer.delete()
        logger.info(f"SBO Officer {officer_username} deleted by superuser {request.user.username}.")
        messages.success(request, "SBO Officer deleted successfully!")
    return redirect('superuser_dashboard')

@user_passes_test(lambda u: u.is_superuser)
def delete_student(request, student_id):
    if request.method == 'POST':
        student = get_object_or_404(Student, id=student_id)
        student_name = student.name
        student.delete()
        logger.info(f"Student {student_name} deleted by superuser {request.user.username}.")
        messages.success(request, "Student deleted successfully!")
    return redirect('superuser_dashboard')