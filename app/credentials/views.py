from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.permissions import role_required
from .models import Credential
from .forms import CredentialForm


@login_required
@role_required('UNIVERSITY_ADMIN')
def issue_credential(request):

    if request.method == 'POST':
        form = CredentialForm(request.POST, university=request.user.university)
        if form.is_valid():
            credential = form.save(commit=False)
            credential.university = request.user.university
            credential.save()
            return redirect('dashboard')
    else:
        form = CredentialForm(university=request.user.university)

    return render(request, 'credentials/issue.html', {'form': form})
