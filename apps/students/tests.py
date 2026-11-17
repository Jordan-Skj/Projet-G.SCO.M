from datetime import date
from io import BytesIO
from tempfile import TemporaryDirectory

from django.contrib import admin
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from apps.accounts.models import CustomUser, Parent
from apps.students.admin import EnrollmentDocumentAdmin
from apps.students.models import (
    AcademicYear,
    Enrollment,
    EnrollmentDocument,
    SchoolClass,
    Student,
    StudentGuardian,
)


class EnrollmentDocumentWorkflowTests(TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        settings_override = override_settings(PRIVATE_MEDIA_ROOT=self.temp_dir.name)
        settings_override.enable()
        self.addCleanup(settings_override.disable)

        self.parent_user = CustomUser.objects.create_user(
            username='documents-parent',
            password='test-password',
            role=CustomUser.Role.PARENT,
        )
        self.parent = Parent.objects.create(
            user=self.parent_user,
            phone_number='0811111111',
            address='Kinshasa',
        )
        self.other_user = CustomUser.objects.create_user(
            username='other-parent',
            password='test-password',
            role=CustomUser.Role.PARENT,
        )
        self.other_parent = Parent.objects.create(
            user=self.other_user,
            phone_number='0822222222',
            address='Kinshasa',
        )
        self.staff = CustomUser.objects.create_user(
            username='admissions-staff',
            password='test-password',
            role=CustomUser.Role.ADMIN,
            is_staff=True,
            is_superuser=True,
        )
        self.year = AcademicYear.objects.create(
            name='2026-2027',
            start_date=date(2026, 9, 1),
            end_date=date(2027, 7, 15),
            is_current=True,
        )
        self.school_class = SchoolClass.objects.create(name='1A')

    @staticmethod
    def photo_upload(name: str = 'photo.png') -> SimpleUploadedFile:
        image_buffer = BytesIO()
        Image.new('RGB', (1, 1), color='white').save(image_buffer, format='PNG')
        return SimpleUploadedFile(name, image_buffer.getvalue(), content_type='image/png')

    @staticmethod
    def certificate_upload(name: str = 'acte.pdf') -> SimpleUploadedFile:
        return SimpleUploadedFile(
            name,
            b'%PDF-1.4 test certificate',
            content_type='application/pdf',
        )

    def registration_data(self) -> dict[str, object]:
        return {
            'first_name': 'Amina',
            'middle_name': 'Marie',
            'last_name': 'Kabeya',
            'date_of_birth': '2015-02-01',
            'gender': Student.Gender.FEMALE,
            'relation': StudentGuardian.Relationship.MOTHER,
            'school_class': self.school_class.pk,
            'birth_certificate': self.certificate_upload(),
            'student_photo': self.photo_upload(),
        }

    def create_enrollment(self) -> Enrollment:
        student = Student.objects.create(
            admission_number='PENDING-TEST-1',
            first_name='Amina',
            last_name='Kabeya',
            date_of_birth=date(2015, 2, 1),
            gender=Student.Gender.FEMALE,
        )
        StudentGuardian.objects.create(
            parent=self.parent,
            student=student,
            relationship=StudentGuardian.Relationship.MOTHER,
        )
        return Enrollment.objects.create(
            student=student,
            school_class=self.school_class,
            academic_year=self.year,
        )

    def create_document(
        self,
        enrollment: Enrollment,
        document_type: str,
        *,
        status: str = EnrollmentDocument.Status.PENDING,
        rejection_reason: str = '',
    ) -> EnrollmentDocument:
        return EnrollmentDocument.objects.create(
            enrollment=enrollment,
            document_type=document_type,
            file=(
                self.photo_upload()
                if document_type == EnrollmentDocument.Type.STUDENT_PHOTO
                else self.certificate_upload()
            ),
            status=status,
            rejection_reason=rejection_reason,
            reviewed_by=self.staff if status != EnrollmentDocument.Status.PENDING else None,
        )

    def test_registration_requires_and_saves_both_documents_privately(self) -> None:
        self.client.force_login(self.parent_user)
        response = self.client.post(
            reverse('student:enroll_child'),
            self.registration_data(),
        )

        self.assertEqual(response.status_code, 201)
        enrollment = Enrollment.objects.get()
        documents = list(enrollment.documents.order_by('document_type'))
        self.assertEqual(len(documents), 2)
        self.assertEqual(enrollment.status, Enrollment.Status.PENDING)
        self.assertTrue(all(document.status == EnrollmentDocument.Status.PENDING for document in documents))

        document_path = documents[0].file.path
        self.assertNotIn('/media/', document_path)
        self.assertTrue(document_path.startswith(self.temp_dir.name))
        self.assertEqual(
            self.client.get(f'/media/{documents[0].file.name}').status_code,
            404,
        )

    def test_registration_rejects_missing_required_document(self) -> None:
        self.client.force_login(self.parent_user)
        data = self.registration_data()
        data.pop('birth_certificate')

        response = self.client.post(reverse('student:enroll_child'), data)

        self.assertEqual(response.status_code, 400)
        self.assertIn('birth_certificate', response.json()['errors'])
        self.assertFalse(Enrollment.objects.exists())

    def test_only_linked_parent_or_staff_can_download_private_documents(self) -> None:
        enrollment = self.create_enrollment()
        document = self.create_document(
            enrollment,
            EnrollmentDocument.Type.BIRTH_CERTIFICATE,
        )
        url = reverse(
            'student:download_enrollment_document',
            kwargs={'document_id': document.pk},
        )

        self.client.force_login(self.other_user)
        self.assertEqual(self.client.get(url).status_code, 403)

        self.client.force_login(self.parent_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Cache-Control'], 'private, no-store')

        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_parent_can_resubmit_rejected_document(self) -> None:
        enrollment = self.create_enrollment()
        rejected = self.create_document(
            enrollment,
            EnrollmentDocument.Type.BIRTH_CERTIFICATE,
            status=EnrollmentDocument.Status.REJECTED,
            rejection_reason="Le document est illisible.",
        )
        self.create_document(enrollment, EnrollmentDocument.Type.STUDENT_PHOTO)
        old_name = rejected.file.name
        self.client.force_login(self.parent_user)

        response = self.client.post(
            reverse(
                'student:resubmit_enrollment_documents',
                kwargs={'enrollment_id': enrollment.pk},
            ),
            {'birth_certificate': self.certificate_upload('acte-corrige.pdf')},
        )

        self.assertEqual(response.status_code, 200)
        rejected.refresh_from_db()
        enrollment.refresh_from_db()
        self.assertEqual(rejected.status, EnrollmentDocument.Status.PENDING)
        self.assertEqual(rejected.rejection_reason, '')
        self.assertIsNone(rejected.reviewed_by)
        self.assertNotEqual(rejected.file.name, old_name)
        self.assertEqual(enrollment.status, Enrollment.Status.PENDING)

    def test_staff_approval_enrolls_only_after_both_documents_are_verified(self) -> None:
        enrollment = self.create_enrollment()
        documents = [
            self.create_document(enrollment, document_type)
            for document_type in EnrollmentDocument.Type
        ]
        model_admin = EnrollmentDocumentAdmin(EnrollmentDocument, admin.site)
        request = RequestFactory().post('/admin/students/enrollmentdocument/')
        request.user = self.staff

        documents[0].status = EnrollmentDocument.Status.APPROVED
        model_admin.save_model(request, documents[0], form=None, change=True)
        enrollment.refresh_from_db()
        self.assertEqual(enrollment.status, Enrollment.Status.PENDING)

        documents[1].status = EnrollmentDocument.Status.APPROVED
        model_admin.save_model(request, documents[1], form=None, change=True)
        enrollment.refresh_from_db()
        self.assertEqual(enrollment.status, Enrollment.Status.ENROLLED)
        self.assertEqual(enrollment.approved_by, self.staff)
        self.assertIsNotNone(enrollment.approved_at)
