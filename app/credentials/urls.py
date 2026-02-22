from django.urls import path
from .views import issue_credential

app_name = "credentials"

urlpatterns = [
    path('issue-credential/', issue_credential, name='issue_credential'),
]
