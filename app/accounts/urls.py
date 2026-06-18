from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "accounts"

urlpatterns = [

    # Student Management
    path(
        'create-student/',
        views.create_student,
        name='create_student'
    ),

    # Dashboards
    path(
        'student-dashboard/',
        views.student_dashboard,
        name='student_dashboard'
    ),

    path(
        'verifier-dashboard/',
        views.verifier_dashboard,
        name='verifier_dashboard'
    ),

    path(
        'university-dashboard/',
        views.university_dashboard,
        name='university_dashboard'
    ),

    path(
        'dashboard/',
        views.dashboard_redirect,
        name='dashboard'
    ),

    # Password Change
    path(
        'change-password/',
        views.change_password,
        name='change_password'
    ),

    # Password Reset
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset.html'
        ),
        name='password_reset'
    ),

    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),

    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]