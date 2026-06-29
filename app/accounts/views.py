from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.permissions import role_required
from .forms import StudentCreationForm
from .decorators import university_admin_required, student_required
from credentials.models import Credential
from .models import AuditLog
from universities.models import UniversityCourse
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
from django.contrib.auth import get_user_model

User = get_user_model()


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
    available_pdfs = credentials.exclude(pdf_file="").exclude(pdf_file__isnull=True).count()
    active_credentials = credentials.filter(is_revoked=False).count()

    return render(
        request,
        "accounts/student_dashboard.html",
        {
            "credentials": credentials,
            "total_credentials": credentials.count(),
            "active_credentials": active_credentials,
            "available_pdfs": available_pdfs,
        }
    )


@login_required
@role_required('UNIVERSITY_ADMIN')
@university_admin_required
def university_dashboard(request):
    university = request.user.university
    credentials = Credential.objects.filter(university=university)
    students = User.objects.filter(role="STUDENT", university=university)

    return render(
        request,
        "accounts/university_dashboard.html",
        {
            "total_students": students.count(),
            "total_credentials": credentials.count(),
            "recent_credentials": credentials.select_related("student").order_by("-created_at")[:5],
        }
    )


@login_required
@role_required('VERIFIER')
def verifier_dashboard(request):
    user = request.user
    verifications = AuditLog.objects.filter(
        user=request.user,
        action='VERIFY_CREDENTIAL'
    )

    total_verifications = verifications.count()
    valid_verifications = verifications.filter(
        description__icontains='Result: VALID'
    ).count() + verifications.filter(
        description__icontains='Result: BLOCKCHAIN_UNAVAILABLE'
    ).count()
    pending_issues = total_verifications - valid_verifications
    recent_verifications = verifications.order_by('-timestamp')[:5]

    return render(
        request,
        "accounts/verifier_dashboard.html",
        {
            "user": user,
            "total_verifications": total_verifications,
            "valid_verifications": valid_verifications,
            "pending_issues": pending_issues,
            "recent_verifications": recent_verifications,
        },
    )


@login_required
@role_required('UNIVERSITY_ADMIN')
@university_admin_required
def create_student(request):

    if request.method == 'POST':
        form = StudentCreationForm(request.POST, university=request.user.university)
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
        form = StudentCreationForm(university=request.user.university)

    return render(request, 'accounts/create_student.html', {'form': form})


@login_required
@role_required('UNIVERSITY_ADMIN')
@university_admin_required
def manage_courses(request):
    university = request.user.university
    courses = UniversityCourse.objects.filter(university=university).order_by('degree_name', 'course_name')

    if request.method == 'POST':
        degree_name = request.POST.get('degree_name', '').strip()
        course_name = request.POST.get('course_name', '').strip()
        field_of_study = request.POST.get('field_of_study', '').strip()

        if not all([degree_name, course_name, field_of_study]):
            messages.error(request, 'Please fill in all course fields.', extra_tags='danger')
        else:
            course, created = UniversityCourse.objects.get_or_create(
                university=university,
                degree_name=degree_name,
                course_name=course_name,
                field_of_study=field_of_study,
            )
            AuditLog.objects.create(
                user=request.user,
                action='ADD_COURSE',
                description=(
                    f"Admin {request.user.username} {'created' if created else 'added'} course "
                    f"{course.degree_name} - {course.course_name} ({course.field_of_study})"
                ),
            )
            messages.success(request, 'Course added successfully.')
            return redirect('accounts:manage_courses')

    return render(request, 'accounts/manage_courses.html', {
        'courses': courses,
    })


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
