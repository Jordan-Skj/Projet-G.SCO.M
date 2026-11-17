from pathlib import Path
from uuid import uuid4

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from apps.accounts.models import Gender, Parent
from .storage import PrivateEnrollmentDocumentStorage


ENROLLMENT_REQUIRED_DOCUMENT_TYPES = (
    'birth_certificate',
    'student_photo',
)


def enrollment_document_upload_to(instance: "EnrollmentDocument", filename: str) -> str:
    extension = Path(filename).suffix.lower()
    return f"{instance.enrollment_id}/{uuid4().hex}{extension}"


# Academic year model
class AcademicYear(models.Model):
    name = models.CharField(max_length=20, unique=True, verbose_name="Année scolaire")
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(verbose_name="Date de fin")
    is_current = models.BooleanField(default=False, verbose_name="Année en cours")
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = "Année scolaire"
        verbose_name_plural = "Années scolaires"
        
    def __str__(self) -> str:
        return self.name
    

# School class model
class SchoolClass(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom de la classe")
    description = models.TextField(blank=True, verbose_name="Description de la classe")

    class Meta:
        ordering = ['name']
        verbose_name = "Classe"
        verbose_name_plural = "Classes"
        
    def __str__(self) -> str:
        return self.name
    

# Student model
class Student(models.Model):
    # Keep the gender choices discoverable through Student for existing callers.
    Gender = Gender

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Actif'
        GRADUATED = 'graduated', 'Diplômé'
        TRANSFERRED = 'transferred', 'Transféré'
        ARCHIVED = 'archived', 'Archivé'
        
    admission_number = models.CharField(max_length=30, unique=True, verbose_name="Matricule")
    first_name = models.CharField(max_length=50, verbose_name="Prénom")
    middle_name = models.CharField(max_length=50, blank=True, verbose_name="Postnom")
    last_name = models.CharField(max_length=50, verbose_name="Nom")
    date_of_birth = models.DateField(verbose_name="Date de naissance")
    gender = models.CharField(max_length=1, choices=Gender.choices, verbose_name="Genre")
    profile_img = models.ImageField(blank=True, null=True, upload_to='students_imgs/')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, verbose_name="Statut")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")
    
    class Meta:
        ordering = ['last_name', "middle_name", 'first_name']
        verbose_name = "Élève"
        verbose_name_plural = "Élèves"
        
    def __str__(self) -> str:
        full_name: str = " ".join(
            part for part in (self.first_name, self.middle_name, self.last_name) if part
        )
        return f"{full_name} | {self.admission_number}"
        
# StudentGuardian model
class StudentGuardian(models.Model):
    class Relationship(models.TextChoices):
        FATHER = 'father', 'Père'
        MOTHER = 'mother', 'Mère'
        GUARDIAN = 'guardian', 'Tuteur légal'
        OTHER = 'other', 'Autre'
        
    parent = models.ForeignKey(Parent, on_delete=models.PROTECT, related_name="student_links")
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="guardian_links")
    relationship = models.CharField(max_length=20, choices=Relationship.choices, verbose_name="Relation avec l'élève")
    is_primary_contact = models.BooleanField(default=False, verbose_name="Contact principal")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_guardian_links", verbose_name="Approuvé par")
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="Approuvé le")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['parent', 'student'], name='unique_parent_student_link'
            )
        ]
        verbose_name = "Lien parent-élève"
        verbose_name_plural = "Liens parent-élève"
        
        
    def __str__(self) -> str:
        return f"{self.parent} - {self.student}"
    
    
# Enrollment model
class Enrollment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', "En attente d'approbation"
        ENROLLED = 'enrolled', "Inscrit"
        APPROVED = 'approved', "Terminé"
        WITHDRAWN = 'withdrawn', "Retiré"

    class PaymentStatus(models.TextChoices):
        PAID = 'paid', "Paye"
        UNPAID = 'unpaid', "Non paye"
        VERIFIED = 'verified', "Verifie"
        
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="enrollments")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="enrollments")
    school_class = models.ForeignKey(SchoolClass, on_delete=models.PROTECT, related_name="enrollments")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name="Statut")
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID, verbose_name="Payment status")
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="approved_enrollments")
    approved_at = models.DateTimeField(null=True, blank=True)
    enrollment_date = models.DateField(auto_now_add=True, verbose_name="Date d'inscription")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'academic_year'], name='unique_student_academic_year_enrollment'
            ),
            models.CheckConstraint(
                condition=~models.Q(status='approved') | models.Q(approved_by__isnull=False, approved_at__isnull=False),
                name='enrollment_approved_needs_approved_by_and_approved_at',
            )
        ]
        verbose_name = "Inscription"
        verbose_name_plural = "Inscriptions"
        ordering = ['school_class', 'academic_year', 'student']
        
    def __str__(self) -> str:
        return f"{self.student} - {self.academic_year} - {self.school_class}"


class EnrollmentDocument(models.Model):
    class Type(models.TextChoices):
        BIRTH_CERTIFICATE = 'birth_certificate', "Acte de naissance"
        STUDENT_PHOTO = 'student_photo', "Photo de l'élève"

    class Status(models.TextChoices):
        PENDING = 'pending', "En attente de vérification"
        APPROVED = 'approved', "Vérifié"
        REJECTED = 'rejected', "À corriger"

    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name="Inscription",
    )
    document_type = models.CharField(
        max_length=30,
        choices=Type.choices,
        verbose_name="Pièce à fournir",
    )
    file = models.FileField(
        storage=PrivateEnrollmentDocumentStorage(),
        upload_to=enrollment_document_upload_to,
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])],
        verbose_name="Fichier",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Statut",
    )
    rejection_reason = models.TextField(blank=True, verbose_name="Motif de rejet")
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="Soumis le")
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='reviewed_enrollment_documents',
        verbose_name="Vérifié par",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="Vérifié le")

    class Meta:
        ordering = ['document_type']
        verbose_name = "Pièce d'inscription"
        verbose_name_plural = "Pièces d'inscription"
        constraints = [
            models.UniqueConstraint(
                fields=['enrollment', 'document_type'],
                name='unique_enrollment_document_type',
            ),
            models.CheckConstraint(
                condition=(
                    ~models.Q(status='rejected')
                    | ~models.Q(rejection_reason='')
                ),
                name='rejected_enrollment_document_needs_reason',
            ),
        ]

    def clean(self) -> None:
        super().clean()
        if self.status == self.Status.REJECTED and not self.rejection_reason.strip():
            raise ValidationError({
                'rejection_reason': "Indiquez les corrections attendues pour cette pièce."
            })

    def __str__(self) -> str:
        return f"{self.get_document_type_display()} — {self.enrollment}"
