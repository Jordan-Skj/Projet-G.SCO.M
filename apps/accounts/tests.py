from datetime import date
from decimal import Decimal

from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import CustomUser, Parent
from apps.finance.models import Fee
from apps.students.models import (
    AcademicYear,
    Enrollment,
    SchoolClass,
    Student,
    StudentGuardian,
)


@override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})
class ParentAccountTests(TestCase):
    def setUp(self) -> None:
        self.user = CustomUser.objects.create_user(
            username='parent-account',
            password='test-password',
            role=CustomUser.Role.PARENT,
        )
        parent = Parent.objects.create(
            user=self.user,
            phone_number='0833333333',
            address='Kinshasa',
        )
        year = AcademicYear.objects.create(
            name='2026-2027',
            start_date=date(2026, 9, 1),
            end_date=date(2027, 7, 15),
            is_current=True,
        )
        school_class = SchoolClass.objects.create(name='2A')
        student = Student.objects.create(
            admission_number='PARENT-001',
            first_name='Amina',
            middle_name='Marie',
            last_name='Kabeya',
            date_of_birth=date(2015, 2, 1),
            gender=Student.Gender.FEMALE,
        )
        StudentGuardian.objects.create(
            parent=parent,
            student=student,
            relationship=StudentGuardian.Relationship.MOTHER,
        )
        self.enrollment = Enrollment.objects.create(
            student=student,
            academic_year=year,
            school_class=school_class,
            status=Enrollment.Status.ENROLLED,
        )
        Fee.objects.create(
            school_class=school_class,
            academic_year=year,
            name='Minerval',
            amount_due=Decimal('100.00'),
            currency=Fee.Currency.USD,
            created_by=self.user,
        )
        self.client.force_login(self.user)

    def test_dashboard_shows_child_data_and_associated_forms(self) -> None:
        response = self.client.get(reverse('account:parent_account'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Amina Marie Kabeya')
        self.assertContains(response, "Dossier d'inscription")
        self.assertContains(response, 'Résultats scolaires')
        self.assertContains(response, 'name="birth_certificate"')
        self.assertContains(response, 'name="student_photo"')
        self.assertContains(response, 'name="fee"')
        self.assertContains(response, 'name="phone_number"')
        self.assertContains(response, 'Envoyer une justification')


@override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})
class ParentSignUpTests(TestCase):
    def test_signup_renders_quarter_field_and_localization_data(self) -> None:
        response = self.client.get(reverse('account:parent_sign_up'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="quarter"')
        self.assertContains(response, 'data-for="quarter"')
        self.assertNotContains(response, 'name="quater"')
        self.assertContains(response, 'KINSHASA_QUARTIERS')

    def test_signup_displays_submission_errors_in_visible_summary(self) -> None:
        response = self.client.post(
            reverse('account:parent_sign_up'),
            {
                'first_name': 'Amina',
                'middle_name': 'Marie',
                'last_name': 'Kabeya',
                'gender': 'F',
                'email': 'not-an-email',
                'phone_number': '812345678',
                'alternate_phone_number': '',
                'township': 'Gombe',
                'quarter': 'Batetela',
                'street': 'Avenue des Ecoles',
                'street_number': '12',
                'password': 'test-password',
                'confirm_password': 'test-password',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="signup-error-summary"')
        self.assertContains(response, 'Email :')
        self.assertContains(response, 'data-error-target="id_email"')
        self.assertContains(response, 'name="quarter"')
        self.assertContains(response, '<option value="Batetela" selected>', html=False)
