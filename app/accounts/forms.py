from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()


class StudentCreationForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control password-input'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            existing_classes = field.widget.attrs.get('class', '')
            class_list = existing_classes.split()
            if 'form-control' not in class_list:
                class_list.append('form-control')
            field.widget.attrs['class'] = ' '.join(class_list)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            try:
                validate_password(password, self.instance)
            except ValidationError as exc:
                raise forms.ValidationError(exc.messages)
        return password

    def save(self, commit=True, university=None):
        user = super().save(commit=False)
        user.role = 'STUDENT'
        user.university = university
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

        return user


class VerifierRegistrationForm(forms.ModelForm):

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control password-input'})
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control password-input'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1:
            try:
                validate_password(password1, self.instance)
            except ValidationError as exc:
                raise forms.ValidationError(exc.messages)
        return password1

    def clean(self):
        cleaned_data = super().clean()

        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Passwords do not match")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'VERIFIER'
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()

        return user


class CustomPasswordChangeForm(PasswordChangeForm):

    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )