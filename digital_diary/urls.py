from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [

    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),

    path('', views.journal_view, name='journal'),
    path('journal/<str:subject>/', views.subject_view, name='subject'),
    path('journal/<str:subject>/<str:class_name>/grades/', views.grades_view, name='grades'),
    path('journal/<str:subject>/<str:class_name>/grades/edit/<int:pk>/', views.grade_edit, name='grade-edit'),
    path('journal/<str:subject>/<str:class_name>/grades/create/<int:student_id>/<str:date>/', views.grade_create, name='grade-create'),
    path('journal/<str:subject>/<str:class_name>/grades/add_date/', views.grade_add_date, name='grade-add-date'),
    path('journal/<str:subject>/<str:class_name>/attendance/', views.attendance_view, name='attendance'),
    path('journal/<str:subject>/<str:class_name>/attendance/edit/<int:pk>/', views.attendance_edit,
         name='attendance-edit'),
    path('journal/<str:subject>/<str:class_name>/attendance/create/<int:student_id>/<str:date>/', views.attendance_create, name='attendance-create'),
    path('journal/<str:subject>/<str:class_name>/attendance/add_date/', views.attendance_add_date, name='attendance-add-date'),

]
