from django.urls import path
from .views import create_student

app_name = "accounts"

urlpatterns = [
    path('create-student/', create_student, name='create_student'),
]
