from django import forms
from .models import Attendance, Grade


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['date', 'present']


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['value']