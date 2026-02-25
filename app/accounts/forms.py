from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class StudentCreationForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control"
            })


    def save(self, commit=True, university=None):
        user = super().save(commit=False)
        user.role = 'STUDENT'
        user.university = university
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
