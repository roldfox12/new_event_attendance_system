from django import forms
from .models import Event, Student, College, SBOOfficer

class AttendanceForm(forms.Form):
    # Define fields first
    event = forms.ModelChoiceField(queryset=Event.objects.none(), empty_label="Select an event")
    id_number = forms.CharField(max_length=20, label="ID Number")
    action = forms.ChoiceField(
        choices=[
            ('am_sign_in', 'AM Sign In'),
            ('am_sign_out', 'AM Sign Out'),
            ('pm_sign_in', 'PM Sign In'),
            ('pm_sign_out', 'PM Sign Out'),
        ],
        label="Action"
    )

    def __init__(self, *args, event_queryset=None, student_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        if event_queryset is not None:
            self.fields['event'].queryset = event_queryset
        if student_queryset is not None:
            self.fields['student'].queryset = student_queryset

class StudentRegistrationForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'id_number', 'college', 'picture']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter student name'}),
            'id_number': forms.TextInput(attrs={'placeholder': 'Enter ID number'}),
            'college': forms.Select(),
            'picture': forms.FileInput(),
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'college', 'date', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter event name'}),
            'college': forms.Select(),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'placeholder': 'Enter event description'}),
        }

class SBOOfficerForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = SBOOfficer
        fields = ['username', 'password', 'college']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter username'}),
            'college': forms.Select(),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data['password']
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'id_number', 'college', 'course', 'school_year', 'picture']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter student name'}),
            'id_number': forms.TextInput(attrs={'placeholder': 'Enter ID number'}),
            'college': forms.Select(),
            'course': forms.TextInput(attrs={'placeholder': 'Enter course'}),
            'school_year': forms.TextInput(attrs={'placeholder': 'Enter school year (e.g., 2023-2024)'}),
            'picture': forms.FileInput(),
        }