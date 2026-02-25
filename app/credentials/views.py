from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from core.permissions import role_required
from .models import Credential
from .forms import CredentialForm
from accounts.decorators import university_admin_required, student_required
from accounts.models import AuditLog
import os
from django.template.loader import render_to_string
from weasyprint import HTML
from django.core.files.base import ContentFile
from django.http import FileResponse, Http404
import os
import tempfile
from django.shortcuts import render, redirect
from django.conf import settings
from PIL import Image
from pyzbar.pyzbar import decode
from pdf2image import convert_from_path


@login_required
@role_required('UNIVERSITY_ADMIN')
@university_admin_required
def issue_credential(request):

    if request.method == 'POST':
        form = CredentialForm(request.POST, university=request.user.university)
        if form.is_valid():
            credential = form.save(commit=False)
            credential.university = request.user.university
            credential.save()

            # Generate PDF

            html_string = render_to_string(
                "credentials/certificate.html",
                {
                    "credential": credential,
                    "qr_path": request.build_absolute_uri(credential.qr_code.url)
                }
            )

            pdf_file = HTML(string=html_string).write_pdf()

            file_name = f"certificate_{credential.id}.pdf"

            credential.pdf_file.save(
                file_name,
                ContentFile(pdf_file),
                save=True
            )

            AuditLog.objects.create(
                user=request.user,
                action='ISSUE_CREDENTIAL',
                credential_id=credential.id,
                student_id=credential.student.id,
                description=f"Credential issued to {credential.student.username}"
            )
            return redirect('dashboard')
    else:
        form = CredentialForm(university=request.user.university)

    return render(request, 'credentials/issue.html', {'form': form})


@student_required
def download_certificate(request, credential_id):

    credential = get_object_or_404(
        Credential,
        id=credential_id,
        student=request.user
    )

    if not credential.pdf_file:
        raise Http404("Certificate not found.")

    return FileResponse(
        credential.pdf_file.open("rb"),
        as_attachment=True,
        filename=credential.pdf_file.name.split("/")[-1]
    )


def upload_and_verify(request):

    if request.method == "POST":
        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            return render(request, "credentials/upload_verify.html", {
                "error": "No file uploaded."
            })

        file_extension = uploaded_file.name.split(".")[-1].lower()

        # Save temporarily
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            for chunk in uploaded_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        qr_data = None

        try:
            # If image
            if file_extension in ["png", "jpg", "jpeg"]:
                image = Image.open(tmp_path)
                decoded = decode(image)
                if decoded:
                    qr_data = decoded[0].data.decode("utf-8")

            # If PDF
            elif file_extension == "pdf":
                images = convert_from_path(tmp_path)
                for img in images:
                    decoded = decode(img)
                    if decoded:
                        qr_data = decoded[0].data.decode("utf-8")
                        break

        finally:
            os.remove(tmp_path)

        if qr_data:
            return redirect(qr_data)

        return render(request, "credentials/upload_verify.html", {
            "error": "QR code not found."
        })

    return render(request, "credentials/upload_verify.html")