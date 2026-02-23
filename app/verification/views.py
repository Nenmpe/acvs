from django.shortcuts import get_object_or_404, render
from credentials.models import Credential
from core.security import verify_signature
import hashlib
from accounts.models import AuditLog


def verify_credential(request, credential_id):

    credential = get_object_or_404(Credential, credential_id=credential_id)

    # Recalculate hash
    data_string = f"{credential.student.username}{credential.degree_name}{credential.field_of_study}{credential.issue_date}{credential.grade}"
    new_hash = hashlib.sha256(data_string.encode()).hexdigest()

    integrity_valid = (new_hash == credential.hash_value)
    
    signature_valid = verify_signature(
        credential.hash_value,
        credential.digital_signature
    )

    if credential.is_revoked:
        status = "REVOKED"
    elif not integrity_valid or not signature_valid:
        status = "TAMPERED"
    else:
        status = "VALID"
    
    
    context = {
        'credential': credential,
        'status': status
    }
    
    AuditLog.objects.create(
        user=None,
        action='VERIFY_CREDENTIAL',
        credential_id=credential.id,
        description=f"Verification attempt. Result: {status}"
    )

    return render(request, 'verification/result.html', context)
