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
from django.urls import reverse
from django.contrib import messages
from core.blockchain import store_hash_on_blockchain


@login_required
@role_required('UNIVERSITY_ADMIN')
@university_admin_required
def issue_credential(request):

    if request.method == 'POST':
        form = CredentialForm(request.POST, university=request.user.university)
        if form.is_valid():
            credential = form.save(commit=False)
            credential.university = request.user.university

            if Credential.objects.filter(
                student=credential.student,
                university=request.user.university
            ).exists():
                messages.error(request, "Credential already issued to this student.")
                return redirect('issue_credential')

            credential.save()

            # Store on blockchain
            tx_hash = store_hash_on_blockchain(credential.credential_hash_value)

            # Save
            credential.blockchain_tx_hash = tx_hash
            credential.save()

            # Generate PDF

            html_string = render_to_string(
                "credentials/certificate.html",
                {
                    "credential": credential,
                    "qr_path": credential.qr_code.path
                }
            )

            html = HTML(
                string=html_string,
                base_url=settings.MEDIA_ROOT
            )

            pdf_file = html.write_pdf()

            # pdf_file = HTML(string=html_string).write_pdf()

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
            messages.success(request, f"Credential issued successfully to {credential.student.username}")
            return redirect('credentials:issue_credential')
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
            verify_url = reverse(
                "verification:verify",
                args=[qr_data]
            )
            return redirect(verify_url)

        return render(request, "credentials/upload_verify.html", {
            "error": "QR code not found."
        })

    return render(request, "credentials/upload_verify.html")