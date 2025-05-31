from django.contrib import admin
from .models import Student, Grade, Attendance


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'class_name')
    search_fields = ('first_name', 'last_name', 'class_name')


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'value', 'date', 'teacher')
    search_fields = ('subject', 'student__last_name', 'student__first_name')
    list_filter = ('subject', 'date')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'present', 'teacher')
    list_filter = ('present', 'date')
