import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from ...models import Student, Grade, Attendance
from faker import Faker

User = get_user_model()

class Command(BaseCommand):
    help = "Заполняет базу данных тестовыми данными для электронного журнала"

    def handle(self, *args, **options):
        fake = Faker('ru_RU')

        # Получаем пользователя-учителя (здесь выбирается первый пользователь с is_staff=True)
        teacher = User.objects.filter(is_staff=True).first()
        if not teacher:
            self.stdout.write(self.style.ERROR("Пользователь-учитель не найден. Создайте хотя бы одного пользователя с is_staff=True."))
            return

        self.stdout.write("Очистка существующих данных...")
        Attendance.objects.all().delete()
        Grade.objects.all().delete()
        Student.objects.all().delete()

        # Создаем учеников
        num_students = 170
        available_classes = ['7А', '7Б', '7В', '8А', '8Б', '8В', '9А', '9Б', '9В',]
        students = []
        for _ in range(num_students):
            student = Student(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                class_name=random.choice(available_classes)
            )
            students.append(student)
        Student.objects.bulk_create(students)
        self.stdout.write(self.style.SUCCESS(f"Создано {num_students} учеников."))

        # Получаем список созданных учеников
        students = list(Student.objects.all())

        subjects = ['Математика', 'Физика', 'История', 'Химия', 'Биология']

        # Создаем оценки для каждого ученика
        grade_list = []
        for student in students:
            # для каждого ученика создаем от 10 до 20 оценок
            for _ in range(random.randint(10, 20)):
                grade = Grade(
                    student=student,
                    teacher=teacher,
                    subject=random.choice(subjects),
                    value=random.randint(2, 5),
                    date=fake.date_between(start_date='-60d', end_date='-30d')
                )
                grade_list.append(grade)
        Grade.objects.bulk_create(grade_list)
        self.stdout.write(self.style.SUCCESS(f"Создано {len(grade_list)} оценок."))

        # Создаем записи посещаемости для каждого ученика
        attendance_list = []
        for student in students:
            # для каждого ученика создаем от 15 до 30 записей посещаемости
            for _ in range(random.randint(15, 30)):
                attendance = Attendance(
                    student=student,
                    teacher=teacher,
                    present=random.choice([True, False]),
                    date=fake.date_between(start_date='-60d', end_date='-30d')
                )
                attendance_list.append(attendance)
        Attendance.objects.bulk_create(attendance_list)
        self.stdout.write(self.style.SUCCESS(f"Создано {len(attendance_list)} записей посещаемости."))

        self.stdout.write(self.style.SUCCESS("Заполнение базы данных завершено!"))
