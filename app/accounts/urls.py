from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path('create-student/', views.create_student, name='create_student'),
    path("dashboard/", views.student_dashboard, name="student_dashboard"),
]
