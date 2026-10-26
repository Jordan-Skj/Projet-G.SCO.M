from django.db import models
from django.conf import settings
from accounts.models import Parent


# Acadenic year model
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
    class Gender(models.TextChoices):
        MALE = 'M', 'Masculin'
        FEMALE = 'F', 'Féminin'
        
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
        ENROLLED = 'enrolled', 'Inscrit'
        COMPLETED = 'completed', 'Terminé'
        WITHDRAWN = 'withdrawn', 'Retiré'
        
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="enrollments")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="enrollments")
    school_class = models.ForeignKey(SchoolClass, on_delete=models.PROTECT, related_name="enrollments")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ENROLLED, verbose_name="Statut")
    enrollment_date = models.DateField(auto_now_add=True, verbose_name="Date d'inscription")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'academic_year'], name='unique_student_academic_year_enrollment'
            )
        ]
        verbose_name = "Inscription"
        verbose_name_plural = "Inscriptions"
        ordering = ["school_class", "academic_year", "student"]
        
    def __str__(self) -> str:
        return f"{self.student} - {self.academic_year} - {self.school_class}"