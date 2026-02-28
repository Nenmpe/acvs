from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.permissions import role_required
from .forms import StudentCreationForm
from .decorators import university_admin_required, student_required
from credentials.models import Credential
from .models import AuditLog
from django.contrib import messages


@student_required
def student_dashboard(request):
    credentials = Credential.objects.filter(student=request.user)

    return render(
        request,
        "accounts/student_dashboard.html",
        {"credentials": credentials}
    )


@login_required
@role_required('UNIVERSITY_ADMIN')
@university_admin_required
def create_student(request):

    if request.method == 'POST':
        form = StudentCreationForm(request.POST)
        if form.is_valid():
            student = form.save(university=request.user.university)
            AuditLog.objects.create(
                user=request.user,
                action='CREATE_STUDENT',
                student_id=student.id,
                description=f"Admin {request.user.username} created student {student.username}"
            )
            messages.success(request, "Student created successfully.")
            return redirect("accounts:create_student")
    else:
        form = StudentCreationForm()

    return render(request, 'accounts/create_student.html', {'form': form})
