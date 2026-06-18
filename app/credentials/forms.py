from django import forms
from .models import Credential
from accounts.models import User

class CredentialForm(forms.ModelForm):

    class Meta:
        model = Credential
        fields = ['student', 'degree_name', 'field_of_study', 'grade', 'issue_date']
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        university = kwargs.pop("university", None)
        super().__init__(*args, **kwargs)

        issued_students = Credential.objects.none()
        if university:
            issued_students = Credential.objects.filter(
                university=university
            ).values_list('student_id', flat=True)

        queryset = User.objects.filter(
                role="STUDENT",
                university=university
            )
        if university:
            queryset = queryset.exclude(id__in=issued_students)

        self.fields['student'].queryset = queryset
