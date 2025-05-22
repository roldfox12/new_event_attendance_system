from django import forms
from .models import Student, Event, College

class StudentRegistrationForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['college', 'id_number', 'name', 'course', 'school_year', 'picture']
        labels = {
            'college': 'College',
            'id_number': 'ID Number',
            'name': 'Full Name',
            'course': 'Course',
            'school_year': 'School Year',
            'picture': 'Profile Picture',
        }

class AttendanceForm(forms.Form):
    event = forms.ModelChoiceField(queryset=Event.objects.all(), label="Select Event")
    id_number = forms.CharField(max_length=50, label="Student ID Number")
    action = forms.ChoiceField(
        choices=[
            ('am_sign_in', 'AM Sign In'),
            ('am_sign_out', 'AM Sign Out'),
            ('pm_sign_in', 'PM Sign In'),
            ('pm_sign_out', 'PM Sign Out'),
        ],
        label="Action"
    )

    def __init__(self, *args, **kwargs):
        event_queryset = kwargs.pop('event_queryset', None)
        super().__init__(*args, **kwargs)
        if event_queryset is not None:
            self.fields['event'].queryset = event_queryset