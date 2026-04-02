from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone

class User(AbstractUser):

    ROLE_CHOICES = (
        ('SUPER_ADMIN', 'Super Admin'),
        ('UNIVERSITY_ADMIN', 'University Admin'),
        ('STUDENT', 'Student'),
        ('VERIFIER', 'Verifier'),
    )

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    university = models.ForeignKey(
        'universities.University',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
    


class AuditLog(models.Model):

    ACTION_CHOICES = (
        ('CREATE_STUDENT', 'Create Student'),
        ('ISSUE_CREDENTIAL', 'Issue Credential'),
        ('REVOKE_CREDENTIAL', 'Revoke Credential'),
        ('VERIFY_CREDENTIAL', 'Verify Credential'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    action = models.CharField(max_length=50, choices=ACTION_CHOICES)

    credential_id = models.IntegerField(null=True, blank=True)
    student_id = models.IntegerField(null=True, blank=True)

    timestamp = models.DateTimeField(default=timezone.now)

    description = models.TextField(blank=True)

    def delete(self, *args, **kwargs):
        raise Exception("Audit logs cannot be deleted")

    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"

