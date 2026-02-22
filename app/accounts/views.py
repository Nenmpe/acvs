from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.permissions import role_required
from .forms import StudentCreationForm


@login_required
@role_required('UNIVERSITY_ADMIN')
def create_student(request):

    if request.method == 'POST':
        form = StudentCreationForm(request.POST)
        if form.is_valid():
            form.save(university=request.user.university)
            return redirect('dashboard')
    else:
        form = StudentCreationForm()

    return render(request, 'accounts/create_student.html', {'form': form})
