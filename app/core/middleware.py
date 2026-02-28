from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

User = get_user_model()


class JWTCookieMiddleware:
    """
    Reads the JWT access token from the HttpOnly cookie and authenticates
    request.user so that all existing @login_required decorators, the Django
    admin panel, and every role-based decorator continue to work unchanged.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            token_str = request.COOKIES.get(settings.JWT_ACCESS_COOKIE)
            if token_str:
                try:
                    token = AccessToken(token_str)
                    user_id = token['user_id']
                    user = User.objects.get(pk=user_id)
                    request.user = user
                except (InvalidToken, TokenError, User.DoesNotExist):
                    request.user = AnonymousUser()

        return self.get_response(request)
