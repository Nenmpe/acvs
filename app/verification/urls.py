from django.urls import path
from .views import verify_credential

app_name = "verification"

urlpatterns = [
    path('verify/<uuid:credential_id>/', verify_credential, name='verify'),
]
