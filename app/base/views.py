from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login as auth_login, logout as auth_logout
from accounts.forms import VerifierRegistrationForm
from credentials.models import Credential
from universities.models import University

User = get_user_model()


def home(request):
    context = {
        "total_credentials": Credential.objects.count(),
        "total_students": User.objects.filter(role="STUDENT").count(),
        "total_universities": University.objects.count(),
        "total_verifiers": User.objects.filter(role="VERIFIER").count(),
        "tamper_detection_rate": "100%",
    }
    return render(request, 'home.html', context)


_COOKIE_KWARGS = dict(path='/', httponly=True, samesite='Lax')


def _set_jwt_cookies(response, user):
    """Issue access + refresh JWT tokens and attach them as HttpOnly cookies."""
    refresh = RefreshToken.for_user(user)
    access_lifetime = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
    refresh_lifetime = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']

    response.set_cookie(
        settings.JWT_ACCESS_COOKIE,
        str(refresh.access_token),
        max_age=int(access_lifetime.total_seconds()),
        secure=not settings.DEBUG,
        **_COOKIE_KWARGS,
    )
    response.set_cookie(
        settings.JWT_REFRESH_COOKIE,
        str(refresh),
        max_age=int(refresh_lifetime.total_seconds()),
        secure=not settings.DEBUG,
        **_COOKIE_KWARGS,
    )


def _delete_jwt_cookies(response):
    """Delete both JWT cookies with the exact same attributes used when setting them."""
    response.delete_cookie(settings.JWT_ACCESS_COOKIE, path='/', samesite='Lax')
    response.delete_cookie(settings.JWT_REFRESH_COOKIE, path='/', samesite='Lax')


# ---------------- LOGIN ----------------
def login(request):
    if request.user.is_authenticated:
        return redirect('base:home')

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user) 
            response = redirect('base:home')
            _set_jwt_cookies(response, user)
            messages.success(request, "Login successful!")
            return response
        else:
            messages.error(request, "Invalid username or password", extra_tags="danger")

    return render(request, "accounts/login.html")


# ---------------- REGISTER ----------------

def register(request):

    if request.user.is_authenticated:
        return redirect('base:home')

    if request.method == 'POST':
        form = VerifierRegistrationForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Verifier account created successfully.')
            return redirect('base:login')
        else:
            # Log errors for debugging and show a message so the template can display field errors
            print("Form is invalid", form.errors.as_json())
            messages.error(request, 'Please correct the errors below.', extra_tags="danger")
    else:
        form = VerifierRegistrationForm()

    return render(request, 'accounts/register.html', {
        'form': form
    })


# ---------------- LOGOUT ----------------
def logout(request):
    # If the request came from the admin panel, send the user back to the admin login page
    referer = request.META.get('HTTP_REFERER', '')
    next_url = '/admin/login/?next=/admin/' if '/admin/' in referer else 'base:home'

    response = redirect(next_url)
    auth_logout(request)
    _delete_jwt_cookies(response)
    messages.success(request, "Logged out successfully")
    return response
