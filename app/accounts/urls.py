from django.urls import path
from .views import create_student

urlpatterns = [
    path('create-student/', create_student, name='create_student'),
]
