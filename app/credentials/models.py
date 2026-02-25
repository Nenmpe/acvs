import uuid
from django.db import models
import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from django.conf import settings
import qrcode
from io import BytesIO
from django.core.files import File


class Credential(models.Model):

    credential_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    hash_value = models.CharField(max_length=256, blank=True)
    digital_signature = models.BinaryField(blank=True, null=True)

    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    university = models.ForeignKey(
        'universities.University',
        on_delete=models.CASCADE
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'STUDENT'}
    )

    degree_name = models.CharField(max_length=255)
    field_of_study = models.CharField(max_length=255)
    grade = models.CharField(max_length=50)
    issue_date = models.DateField()

    is_revoked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    pdf_file = models.FileField(
        upload_to="certificates/",
        null=True,
        blank=True
    )


    def generate_qr(self):
        verification_url = f"{settings.BASE_URL}/verify/{self.credential_id}/"
        qr = qrcode.make(verification_url)

        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        file_name = f'qr_{self.credential_id}.png'

        self.qr_code.save(file_name, File(buffer), save=False)


    def generate_hash(self):
        data_string = f"{self.student.username}{self.degree_name}{self.field_of_study}{self.issue_date}{self.grade}"
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    def sign_credential(self):

        with open("private_key.pem", "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
            )

        signature = private_key.sign(
            self.hash_value.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )

        return signature
    
    def save(self, *args, **kwargs):
        # Only generate hash + signature on first creation
        if not self.pk:
            self.hash_value = self.generate_hash()
            super().save(*args, **kwargs)

            self.digital_signature = self.sign_credential()
            super().save(update_fields=["digital_signature"])

            # Generate QR only once
            if not self.qr_code:
                self.generate_qr()
                super().save(update_fields=["qr_code"])
        else:
            super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.student.username} - {self.degree_name}"
