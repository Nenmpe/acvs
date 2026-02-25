from django import forms
from .models import Credential
from accounts.models import User

class CredentialForm(forms.ModelForm):

    class Meta:
        model = Credential
        fields = ['student', 'degree_name', 'field_of_study', 'grade', 'issue_date']

    def __init__(self, *args, **kwargs):
        university = kwargs.pop("university", None)
        super().__init__(*args, **kwargs)

        if university:
            self.fields['student'].queryset = User.objects.filter(
                role="STUDENT",
                university=university
            )