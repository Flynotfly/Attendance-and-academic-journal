from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    first_name = models.CharField("Имя", max_length=50)
    last_name = models.CharField("Фамилия", max_length=50)
    class_name = models.CharField("Класс", max_length=20)

    class Meta:
        indexes = [models.Index(fields=["class_name", "last_name", "first_name"])]
        ordering = ["class_name", "last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField("Предмет", max_length=100)
    value = models.IntegerField("Оценка")
    date = models.DateField("Дата")

    def __str__(self):
        return f"{self.subject}: {self.value} ({self.student})"


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField("Дата")
    present = models.BooleanField("Присутствовал", default=True)

    def __str__(self):
        status = "Присутствует" if self.present else "Отсутствует"
        return f"{self.student} - {self.date} - {status}"
