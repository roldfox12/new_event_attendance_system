from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import AttendanceForm, StudentRegistrationForm
from .models import Event, Attendance, Student
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
    receipt_data = request.session.get('receipt_data')

    if request.method == 'POST':
        form = AttendanceForm(request.POST, event_queryset=events)
        if form.is_valid():
            id_number = form.cleaned_data['id_number']
            event = form.cleaned_data['event']
            action = request.POST.get('action')

            try:
                student = Student.objects.get(id_number=id_number, college=officer.college)
            except Student.DoesNotExist:
                messages.error(request, "Student not found in your college or not registered.")
                return redirect('attendance_form')

            try:
                existing_attendance = Attendance.objects.get(student=student, event=event)
                if action == 'sign_in' and existing_attendance.sign_in_time and existing_attendance.sign_out_time:
                    messages.error(request, f"{student.name} has already signed in and out for this event.")
                    return redirect('attendance_form')
            except Attendance.DoesNotExist:
                existing_attendance = None

            if action == 'sign_in':
                if existing_attendance:
                    if existing_attendance.sign_in_time and not existing_attendance.sign_out_time:
                        messages.warning(request, f"{student.name} is already signed in.")
                        receipt_data = {
                            'action': 'Sign In',
                            'time': existing_attendance.sign_in_time.strftime('%Y-%m-%d %H:%M:%S'),
                            'sign_in_time': existing_attendance.sign_in_time.strftime('%Y-%m-%d %H:%M:%S'),  # Add sign_in_time
                            'student_name': student.name,
                            'id_number': student.id_number,
                            'college': student.college.name,
                            'event_name': event.name,
                        }
                    else:
                        pass
                else:
                    attendance = Attendance.objects.create(
                        student=student,
                        event=event,
                        sign_in_time=timezone.now()
                    )
                    messages.success(request, f"{student.name} signed in successfully!")
                    receipt_data = {
                        'action': 'Sign In',
                        'time': attendance.sign_in_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'sign_in_time': attendance.sign_in_time.strftime('%Y-%m-%d %H:%M:%S'),  # Add sign_in_time
                        'student_name': student.name,
                        'id_number': student.id_number,
                        'college': student.college.name,
                        'event_name': event.name,
                    }
            elif action == 'sign_out':
                if not existing_attendance:
                    messages.error(request, "No sign-in record found for this student and event.")
                elif existing_attendance.sign_out_time:
                    messages.warning(request, f"{student.name} has already signed out.")
                    receipt_data = {
                        'action': 'Sign Out',
                        'time': existing_attendance.sign_out_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'sign_in_time': existing_attendance.sign_in_time.strftime('%Y-%m-%d %H:%M:%S') if existing_attendance.sign_in_time else 'N/A',  # Add sign_in_time
                        'student_name': student.name,
                        'id_number': student.id_number,
                        'college': student.college.name,
                        'event_name': event.name,
                    }
                else:
                    existing_attendance.sign_out_time = timezone.now()
                    existing_attendance.save()
                    messages.success(request, f"{student.name} signed out successfully!")
                    receipt_data = {
                        'action': 'Sign Out',
                        'time': existing_attendance.sign_out_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'sign_in_time': existing_attendance.sign_in_time.strftime('%Y-%m-%d %H:%M:%S') if existing_attendance.sign_in_time else 'N/A',  # Add sign_in_time
                        'student_name': student.name,
                        'id_number': student.id_number,
                        'college': student.college.name,
                        'event_name': event.name,
                    }

            if receipt_data:
                request.session['receipt_data'] = receipt_data

    return render(request, 'attendance/attendance_form.html', {
        'form': form,
        'receipt_data': receipt_data,
    })

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

@login_required(login_url='sbo_login')
def print_receipt(request):
    receipt_data = request.session.get('receipt_data')
    if not receipt_data:
        messages.error(request, "No receipt data available. Please sign in or out first.")
        return redirect('attendance_form')
    return render(request, 'attendance/receipt.html', {'receipt_data': receipt_data})