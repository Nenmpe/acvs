from datetime import date

from django.contrib import admin
from django.test import RequestFactory, TestCase

from accounts.admin import AuditLogAdmin, StudentAdmin, UniversityAdminAdmin
from accounts.models import AuditLog, Student, UniversityAdmin, User
from credentials.admin import CredentialAdmin
from credentials.models import Credential
from universities.admin import UniversityAdmin as UniversityModelAdmin
from universities.models import University


class UniversityAdminScopeTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.abc = University.objects.create(
            name="ABC University",
            email="abc@example.com",
            address="ABC Road",
        )
        self.xyz = University.objects.create(
            name="XYZ University",
            email="xyz@example.com",
            address="XYZ Road",
        )
        self.abc_admin = User.objects.create_user(
            username="abc-admin",
            email="abc-admin@example.com",
            password="password",
            role="UNIVERSITY_ADMIN",
            university=self.abc,
            is_staff=True,
        )
        self.abc_student = User.objects.create_user(
            username="abc-student",
            email="abc-student@example.com",
            password="password",
            role="STUDENT",
            university=self.abc,
        )
        self.xyz_student = User.objects.create_user(
            username="xyz-student",
            email="xyz-student@example.com",
            password="password",
            role="STUDENT",
            university=self.xyz,
        )
        Credential.objects.bulk_create([
            Credential(
                university=self.abc,
                student=self.abc_student,
                degree_name="BCA",
                field_of_study="Computer Applications",
                grade="A",
                issue_date=date(2026, 1, 1),
            ),
            Credential(
                university=self.xyz,
                student=self.xyz_student,
                degree_name="BBA",
                field_of_study="Business",
                grade="A",
                issue_date=date(2026, 1, 1),
            ),
            Credential(
                university=self.abc,
                student=self.xyz_student,
                degree_name="Mismatched Degree",
                field_of_study="Bad Data",
                grade="A",
                issue_date=date(2026, 1, 1),
            ),
        ])
        self.abc_credential = Credential.objects.get(
            university=self.abc,
            student=self.abc_student,
        )
        self.xyz_credential = Credential.objects.get(
            university=self.xyz,
            student=self.xyz_student,
        )
        self.mismatched_credential = Credential.objects.get(
            university=self.abc,
            student=self.xyz_student,
        )

    def _request_for_abc_admin(self):
        request = self.factory.get("/admin/")
        request.user = self.abc_admin
        return request

    def test_student_admin_only_shows_same_university_students(self):
        model_admin = StudentAdmin(Student, admin.site)

        usernames = set(
            model_admin.get_queryset(self._request_for_abc_admin())
            .values_list("username", flat=True)
        )

        self.assertEqual(usernames, {"abc-student"})
        self.assertTrue(
            model_admin.has_view_permission(
                self._request_for_abc_admin(),
                self.abc_student,
            )
        )
        self.assertFalse(
            model_admin.has_view_permission(
                self._request_for_abc_admin(),
                self.xyz_student,
            )
        )

    def test_credential_admin_only_shows_same_university_credentials(self):
        model_admin = CredentialAdmin(Credential, admin.site)

        student_usernames = set(
            model_admin.get_queryset(self._request_for_abc_admin())
            .values_list("student__username", flat=True)
        )

        self.assertEqual(student_usernames, {"abc-student"})
        self.assertTrue(
            model_admin.has_view_permission(
                self._request_for_abc_admin(),
                self.abc_credential,
            )
        )
        self.assertFalse(
            model_admin.has_view_permission(
                self._request_for_abc_admin(),
                self.xyz_credential,
            )
        )
        self.assertFalse(
            model_admin.has_view_permission(
                self._request_for_abc_admin(),
                self.mismatched_credential,
            )
        )

    def test_university_admin_only_sees_students_and_credentials_modules(self):
        request = self._request_for_abc_admin()

        self.assertTrue(StudentAdmin(Student, admin.site).has_module_permission(request))
        self.assertTrue(CredentialAdmin(Credential, admin.site).has_module_permission(request))
        self.assertFalse(
            AuditLogAdmin(AuditLog, admin.site).has_module_permission(request)
        )
        self.assertFalse(
            UniversityAdminAdmin(UniversityAdmin, admin.site).has_module_permission(request)
        )
        self.assertFalse(
            UniversityModelAdmin(University, admin.site).has_module_permission(request)
        )

    def test_hidden_modules_are_not_accessible_by_direct_object_permission(self):
        request = self._request_for_abc_admin()

        self.assertFalse(
            AuditLogAdmin(AuditLog, admin.site).has_view_permission(request)
        )
        self.assertFalse(
            UniversityAdminAdmin(UniversityAdmin, admin.site).has_view_permission(
                request,
                self.abc_admin,
            )
        )
        self.assertFalse(
            UniversityModelAdmin(University, admin.site).has_view_permission(
                request,
                self.abc,
            )
        )
