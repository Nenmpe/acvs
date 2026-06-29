import json

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
        self.fields['student'].widget.attrs.update({
            'class': 'form-select form-select-lg'
        })
        self.fields['degree_name'].required = False
        self.fields['degree_name'].label = 'Degree / Course'
        self.fields['degree_name'].widget.attrs.update({
            'class': 'form-control form-control-lg bg-body-tertiary text-body border-0 shadow-none',
            'readonly': 'readonly',
            'placeholder': 'Select a student to auto-fill this field'
        })
        self.fields['field_of_study'].required = False
        self.fields['field_of_study'].label = 'Field of Study'
        self.fields['field_of_study'].widget.attrs.update({
            'class': 'form-control form-control-lg bg-body-tertiary text-body border-0 shadow-none',
            'readonly': 'readonly',
            'placeholder': 'Select a student to auto-fill this field'
        })
        self.fields['grade'].widget.attrs.update({
            'class': 'form-control form-control-lg bg-body-tertiary text-body border-0 shadow-sm'
        })
        self.fields['issue_date'].widget.attrs.update({
            'class': 'form-control form-control-lg bg-body-tertiary text-body border-0 shadow-sm'
        })

        student_course_data = {}
        for student in queryset:
            course = getattr(student, 'course', None)
            student_course_data[str(student.id)] = {
                'degree_name': course.degree_name if course else '',
                'field_of_study': course.field_of_study if course else '',
            }
        self.student_course_data = student_course_data

        student_id = self.data.get('student') or self.initial.get('student')
        if student_id:
            student = queryset.filter(id=student_id).first()
            self._set_student_course_details(student)
        else:
            self._set_student_course_details(None)

    def _set_student_course_details(self, student):
        degree_value = ''
        field_value = ''

        if student and getattr(student, 'course', None):
            course = student.course
            degree_value = course.degree_name
            field_value = course.field_of_study

        self.initial['degree_name'] = degree_value
        self.initial['field_of_study'] = field_value
        self.fields['degree_name'].initial = degree_value
        self.fields['field_of_study'].initial = field_value

        if self.is_bound:
            data = self.data.copy()
            data['degree_name'] = degree_value
            data['field_of_study'] = field_value
            self.data = data

    def save(self, commit=True):
        instance = super().save(commit=False)
        student = self.cleaned_data.get('student')

        if student and getattr(student, 'course', None):
            instance.course = student.course
            instance.degree_name = student.course.degree_name
            instance.field_of_study = student.course.field_of_study

        if commit:
            instance.save()

        return instance
