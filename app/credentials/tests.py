from django.test import TestCase

from .forms import CredentialForm


class CredentialFormTests(TestCase):
    def test_student_course_data_is_a_dictionary_for_template_script(self):
        form = CredentialForm(university=None)

        self.assertIsInstance(form.student_course_data, dict)
        self.assertEqual(form.student_course_data, {})
