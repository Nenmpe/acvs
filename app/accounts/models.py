from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):

    ROLE_CHOICES = (
        ('SUPER_ADMIN', 'Super Admin'),
        ('UNIVERSITY_ADMIN', 'University Admin'),
        ('STUDENT', 'Student'),
        ('VERIFIER', 'Verifier'),
    )

    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    university = models.ForeignKey(
        'universities.University',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.username} ({self.role})"

