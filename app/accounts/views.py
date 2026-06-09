from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.permissions import role_required
from .forms import StudentCreationForm
from .decorators import university_admin_required, student_required
from credentials.models import Credential
from .models import AuditLog
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import (
        PasswordChangeView,
        PasswordResetView,
        PasswordResetDoneView,
        PasswordResetConfirmView,
        PasswordResetCompleteView
    )
from django.urls import reverse_lazy
from django.contrib.auth import update_session_auth_hash
from .forms import CustomPasswordChangeForm


@login_required
def dashboard_redirect(request):

    if request.user.role == 'STUDENT':
        return redirect('accounts:student_dashboard')

    elif request.user.role == 'VERIFIER':
        return redirect('accounts:verifier_dashboard')

    elif request.user.role == 'UNIVERSITY_ADMIN':
        return redirect('accounts:university_dashboard')

    elif request.user.role == 'SUPER_ADMIN':
        return redirect('/admin/')

    return redirect('base:home')


@student_required
def student_dashboard(request):
    credentials = Credential.objects.filter(student=request.user)

    return render(
        request,
        "accounts/student_dashboard.html",
        {"credentials": credentials}
    )


def university_dashboard(request):
    # credentials = Credential.objects.filter(student=request.user)

    return render(
        request,
        "accounts/university_dashboard.html",
        # {"credentials": credentials}
    )


def verifier_dashboard(request):
    user = request.user
    
    return render(
        request,
        "accounts/verifier_dashboard.html",
        {
            "user": user
        },
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


@login_required
def change_password(request):

    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully.')
            return redirect('accounts:dashboard')

    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {
        'form': form
    })
