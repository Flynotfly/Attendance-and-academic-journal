from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime

from .models import Grade, Attendance, Student
from .forms import GradeForm


@login_required
def journal_view(request):
    """
    Главная страница электронного журнала.
    Выводит список уникальных предметов, по которым учитель имеет записи (например, оценки).
    """
    subjects = Grade.objects.filter(teacher=request.user).values_list('subject', flat=True).distinct()
    return render(request, 'journal.html', {'subjects': subjects})


@login_required
def subject_view(request, subject):
    """
    Страница выбранного предмета.
    Выводит список классов (значение поля student__class_name) для данного предмета, где учитель имеет записи.
    """
    classes = Grade.objects.filter(teacher=request.user, subject=subject).values_list('student__class_name', flat=True).distinct()
    return render(request, 'subject.html', {'subject': subject, 'classes': classes})


@login_required
def attendance_view(request, subject, **kwargs):
    class_name = kwargs.get('class_name')
    students = Student.objects.filter(class_name=class_name)
    attendance_qs = Attendance.objects.filter(
        teacher=request.user,
        student__class_name=class_name
    )
    # Вычисляем уникальные даты записей посещаемости
    distinct_dates = sorted({att.date for att in attendance_qs})

    # Формируем структуру: по умолчанию для каждой даты ставим '-'
    table_data = {}
    for student in students:
        # Initialize each cell as None to indicate no record exists
        table_data[student.id] = {d: None for d in distinct_dates}
    for att in attendance_qs:
        # Populate cell with a dictionary that holds the attendance record details
        table_data[att.student.id][att.date] = {
            'status': '+' if att.present else '-',
            'id': att.pk,
        }

    context = {
        'subject': subject,
        'class_name': class_name,
        'students': students,
        'dates': distinct_dates,
        'table_data': table_data,
    }
    return render(request, 'attendance.html', context)


@login_required
def attendance_edit(request, subject, class_name, pk):
    """
    Toggle the attendance record between present and absent.
    """
    attendance_record = get_object_or_404(Attendance, pk=pk, teacher=request.user)
    attendance_record.present = not attendance_record.present
    attendance_record.save()
    return redirect('attendance', subject=subject, class_name=class_name)


@login_required
def attendance_create(request, subject, class_name, student_id, date):
    student = get_object_or_404(Student, id=student_id, class_name=class_name)
    attendance_date = datetime.strptime(date, '%Y-%m-%d').date()
    Attendance.objects.get_or_create(
        student=student,
        teacher=request.user,
        date=attendance_date,
        defaults={'present': True}
    )
    return redirect('attendance', subject=subject, class_name=class_name)


@login_required
def attendance_add_date(request, subject, class_name):
    """
    View to add attendance for a new date for all students in a class.
    The teacher selects a date and marks each student as present (checkbox checked) or absent.
    """
    students = Student.objects.filter(class_name=class_name)

    if request.method == 'POST':
        # Get the date string from the form and convert it to a date object.
        date_str = request.POST.get('date')
        try:
            attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            error = "Неверный формат даты. Используйте ГГГГ-ММ-ДД."
            return render(request, 'attendance_add_date.html', {
                'error': error,
                'subject': subject,
                'class_name': class_name,
                'students': students,
            })

        # Loop over each student and create or update the attendance record.
        for student in students:
            # Check if the checkbox was ticked for this student.
            # Note: When unchecked, the checkbox value is not sent, so get() returns None.
            present = request.POST.get(f'student_{student.id}') == 'on'
            # Create a new record if one does not exist for this student on this date.
            attendance, created = Attendance.objects.get_or_create(
                student=student,
                teacher=request.user,
                date=attendance_date,
                defaults={'present': present},
            )
            # If a record exists, update its status based on the form.
            if not created:
                attendance.present = present
                attendance.save()
        return redirect('attendance', subject=subject, class_name=class_name)

    # For GET requests, simply render the form.
    return render(request, 'attendance_add_date.html', {
        'subject': subject,
        'class_name': class_name,
        'students': students,
    })


@login_required
def grades_view(request, subject, **kwargs):
    # Получаем имя класса (используем kwargs, т.к. class – зарезервированное слово)
    class_name = kwargs.get('class_name')
    # Получаем всех учеников класса
    students = Student.objects.filter(class_name=class_name)
    # Получаем оценки для текущего учителя, предмета и класса
    grades_qs = Grade.objects.filter(
        teacher=request.user,
        subject=subject,
        student__class_name=class_name
    )
    # Вычисляем уникальные даты оценок и сортируем их
    distinct_dates = sorted({grade.date for grade in grades_qs})

    # Формируем структуру: {student_id: {date: [grade_obj1, grade_obj2, ...], ...}, ...}
    table_data = {}
    for student in students:
        table_data[student.id] = {d: [] for d in distinct_dates}
    for grade in grades_qs:
        table_data[grade.student.id][grade.date].append(grade)

    context = {
        'subject': subject,
        'class_name': class_name,
        'students': students,
        'dates': distinct_dates,
        'table_data': table_data,
    }
    return render(request, 'grades.html', context)


@login_required
def grade_edit(request, subject, class_name, pk):
    """
    Edit an existing grade record.
    """
    grade_record = get_object_or_404(Grade, pk=pk, teacher=request.user)
    if request.method == 'POST':
        form = GradeForm(request.POST, instance=grade_record)
        if form.is_valid():
            form.save()
            return redirect('grades', subject=subject, class_name=class_name)
    else:
        form = GradeForm(instance=grade_record)
    return render(request, 'grade_edit.html', {
        'form': form,
        'subject': subject,
        'class_name': class_name,
    })


@login_required
def grade_create(request, subject, class_name, student_id, date):
    """
    Create a new grade record for the given student on the specified date.
    """
    student = get_object_or_404(Student, pk=student_id, class_name=class_name)
    try:
        grade_date = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        # Если формат даты неверный, можно перенаправить обратно
        return redirect('grades', subject=subject, class_name=class_name)

    if request.method == 'POST':
        form = GradeForm(request.POST)
        if form.is_valid():
            new_grade = form.save(commit=False)
            new_grade.student = student
            new_grade.teacher = request.user
            new_grade.subject = subject
            new_grade.date = grade_date
            new_grade.save()
            return redirect('grades', subject=subject, class_name=class_name)
    else:
        form = GradeForm()
    return render(request, 'grade_create.html', {
        'form': form,
        'subject': subject,
        'class_name': class_name,
        'student': student,
        'date': date,
    })


@login_required
def grade_add_date(request, subject, class_name):
    """
    Add grades for a new date for all students in the class.
    Teacher selects a date and enters grade values (or leaves blank to skip).
    """
    students = Student.objects.filter(class_name=class_name)
    if request.method == 'POST':
        date_str = request.POST.get('date')
        try:
            grade_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            error = "Неверный формат даты. Используйте ГГГГ-ММ-ДД."
            return render(request, 'grade_add_date.html', {
                'error': error,
                'subject': subject,
                'class_name': class_name,
                'students': students,
            })
        # Для каждого ученика создаём новую оценку, если введено значение
        for student in students:
            value = request.POST.get(f'student_{student.id}')
            if value:
                try:
                    value_int = int(value)
                    Grade.objects.create(
                        student=student,
                        teacher=request.user,
                        subject=subject,
                        value=value_int,
                        date=grade_date
                    )
                except ValueError:
                    # Если значение не является числом, пропускаем или логируем ошибку
                    continue
        return redirect('grades', subject=subject, class_name=class_name)
    return render(request, 'grade_add_date.html', {
        'subject': subject,
        'class_name': class_name,
        'students': students,
    })
