from django.urls import path
from .views import issue_credential, download_certificate, upload_and_verify

app_name = "credentials"

urlpatterns = [
    path('issue-credential/', issue_credential, name='issue_credential'),
    path(
        "download/<int:credential_id>/",
        download_certificate,
        name="download_certificate"
    ),
    path(
        "upload-verify/",
        upload_and_verify,
        name="upload_verify"
    ),
]
