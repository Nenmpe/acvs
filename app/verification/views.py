from django.contrib import messages
from django.shortcuts import redirect, render
from credentials.models import Credential
from core.security import verify_signature
from accounts.models import AuditLog
from core.blockchain import (
    verify_hash_on_blockchain,
    BLOCKCHAIN_CONFIRMED,
    BLOCKCHAIN_INVALID,
    BLOCKCHAIN_PENDING,
    BLOCKCHAIN_UNAVAILABLE,
)
from core.utils.credintial_hash import generate_credential_hash


def verify_credential(request, credential_id):

    credential = Credential.objects.filter(credential_id=credential_id).first()

    if not credential:
        messages.error(request, "Credential not Found.", extra_tags="danger")
        return redirect("credentials:upload_verify")

    blockchain_status = verify_hash_on_blockchain(
        credential.blockchain_tx_hash,
        credential.credential_hash_value
    )

    new_hash = generate_credential_hash(credential).strip().lower()
    integrity_valid = (new_hash == credential.credential_hash_value.strip().lower())

    signature_valid = verify_signature(
        credential.credential_hash_value,
        credential.digital_signature
    )

    blockchain_pending = False

    if credential.is_revoked:
        status = "REVOKED"
    elif blockchain_status == BLOCKCHAIN_INVALID:
        status = "TAMPERED"
    elif blockchain_status == BLOCKCHAIN_PENDING:
        blockchain_pending = True
        status = "VALID" if integrity_valid and signature_valid else "TAMPERED"
    elif blockchain_status == BLOCKCHAIN_CONFIRMED:
        status = "VALID" if integrity_valid and signature_valid else "TAMPERED"
    elif blockchain_status == BLOCKCHAIN_UNAVAILABLE:
        if integrity_valid and signature_valid:
            status = "BLOCKCHAIN_UNAVAILABLE"
        else:
            status = "TAMPERED"
    else:
        status = "TAMPERED"

    audit_description = f"Verification attempt. Result: {status}"
    if blockchain_pending:
        audit_description += " (blockchain confirmation pending)"
    elif status == "BLOCKCHAIN_UNAVAILABLE":
        audit_description += " (blockchain network unreachable; verified locally only)"

    context = {
        'credential': credential,
        'status': status,
        'blockchain_pending': blockchain_pending,
    }

    AuditLog.objects.create(
        user=request.user if request.user else None,
        action='VERIFY_CREDENTIAL',
        credential_id=credential.id,
        description=audit_description
    )

    return render(request, 'verification/result.html', context)
