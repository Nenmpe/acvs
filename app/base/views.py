from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login as auth_login, logout as auth_logout
from accounts.forms import VerifierRegistrationForm

User = get_user_model()


def home(request):
    return render(request, 'home.html')


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
        form = VerifierRegistrationForm()

    return render(request, 'accounts/register.html', {
        'form': form
    })


'''def register(request):
    if request.user.is_authenticated:
        return redirect('base:home')

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect('register')

        User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        messages.success(request, "Account created successfully! Please login.")
        return redirect('base:login')

    return render(request, "accounts/register.html")'''


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