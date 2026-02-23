from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.permissions import role_required
from .models import Credential
from .forms import CredentialForm
from accounts.decorators import university_admin_required
from accounts.models import AuditLog


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
