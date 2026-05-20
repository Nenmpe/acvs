from django.shortcuts import get_object_or_404, render
from credentials.models import Credential
from core.security import verify_signature
import hashlib
from accounts.models import AuditLog
from core.blockchain import verify_hash_on_blockchain
from core.utils.credintial_hash import generate_credential_hash


def verify_credential(request, credential_id):

    credential = get_object_or_404(Credential, credential_id=credential_id)

    integrity_valid = False
    signature_valid = False

    # First verify in blockchain
    try:
        blockchain_is_valid = verify_hash_on_blockchain(
            credential.blockchain_tx_hash,
            credential.credential_hash_value
        )
    except Exception:
        blockchain_is_valid = False

    if blockchain_is_valid:
        # Recalculate hash
        new_hash = generate_credential_hash(credential).strip().lower()
        # data_string = f"{credential.student.username}{credential.degree_name}{credential.field_of_study}{credential.issue_date}{credential.grade}"
        # new_hash = hashlib.sha256(data_string.encode()).hexdigest()

        integrity_valid = (new_hash == credential.credential_hash_value.strip().lower())

    
    signature_valid = verify_signature(
        credential.credential_hash_value,
        credential.digital_signature
    )

    if credential.is_revoked:
        status = "REVOKED"
    elif not blockchain_is_valid or not integrity_valid or not signature_valid:
        status = "TAMPERED"
    else:
        status = "VALID"
    
    
    context = {
        'credential': credential,
        'status': status
    }
    
    AuditLog.objects.create(
        user= request.user if request.user else None,
        action='VERIFY_CREDENTIAL',
        credential_id=credential.id,
        description=f"Verification attempt. Result: {status}"
    )

    return render(request, 'verification/result.html', context)
