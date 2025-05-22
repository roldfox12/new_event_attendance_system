from django.contrib import admin
from django import forms
from .models import College, Student, Event, Attendance, SBOOfficer

class SBOOfficerAdminForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=False, label="Confirm Password")

    class Meta:
        model = SBOOfficer
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)  # Hash the password
        if commit:
            user.save()
        return user
    
@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'id_number', 'college', 'course', 'school_year', 'created_at']
    list_filter = ['college', 'course', 'school_year']
    search_fields = ['name', 'id_number']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'college', 'date', 'created_at']
    list_filter = ['college', 'date']
    search_fields = ['name']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'event', 'am_sign_in_time', 'am_sign_out_time','pm_sign_in_time','pm_sign_out_time', 'created_at']
    list_filter = ['event', 'student']
    search_fields = ['student__name', 'event__name']
    list_per_page = 25

@admin.register(SBOOfficer)
class SBOOfficerAdmin(admin.ModelAdmin):
    form = SBOOfficerAdminForm  # Assign the custom form here
    list_display = ['username', 'college', 'is_active', 'is_admin']
    list_filter = ['college', 'is_active', 'is_admin']
    search_fields = ['username']

    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new user
            obj.set_password(form.cleaned_data['password'])
        elif form.cleaned_data['password']:  # If updating and password is provided
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)