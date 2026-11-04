from django.db import models
from django.conf import settings

from accounts.models import Gender
from students.models import SchoolClass

class Teacher(models.Model):
    class StudiesDegree(models.TextChoices):
        PRIMARY = 'primary', "Primaire "
        SECONDARY = 'secondary', "Secondaire "
        KINDERGARTEN = 'kindegarten', "Maternelle"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    gender = models.CharField(max_length=30, choices=Gender.choices, verbose_name="Sexe")
    studies_degree = models.CharField(max_length=40, choices=StudiesDegree.choices)
    birth_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Professeur"
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name} :{'professeur' if self.studies_degree.lower() != 'maternelle' else 'maitresse' } de la {self.studies_degree.lower()}"


class Course(models.Model):
    name = models.CharField(max_length=120, verbose_name="Nom du cours")
    school_class = models.ForeignKey(SchoolClass, on_delete=models.PROTECT, verbose_name="Classe")
    teacher = models.ForeignKey(Teacher, on_delete=models.PROTECT, verbose_name="Professeur en charge")
    max_points = models.IntegerField(default=0, verbose_name="Max points")
    chapter_nb = models.IntegerField(default=0, verbose_name="Nombre de chapitre")

    class Meta:
        verbose_name = "Cours"
        ordering = ['name', 'max_points']


class Lesson(models.Model):
    class Status(models.TextChoices):
        APPROVED = 'approved', "Approuve"
        PENDING = 'pending', "En cours de verification"
        SEEN = 'seen', "Vue"
        VOID = 'void', "Annule"

    title = models.CharField(max_length=190, verbose_name="Titre de la lecon")
    description = models.TextField(verbose_name="Description de la lecon")
    explanation = models.TextField(verbose_name="Explication clee de la lecon")
    course = models.ForeignKey(Course, on_delete=models.PROTECT, verbose_name="Cours")
    status = models.CharField(max_length=50, verbose_name="Status")
    course_chapter = models.IntegerField(default=0, verbose_name="Chapitre n*")
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, blank=True, null=True)

    class Meta:
        verbose_name = "Lecon"
        ordering = ['title', '-created_at']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(status='approved') & (models.Q(approved_by__isnull=False) | models.Q(approved_at__isnull=False)),
                name='lesson_approved_needs_approved_by_and_approved_at'
            )
        ]


class Test(models.Model):
    class Type(models.TextChoices):
        EXAM = 'exam', "Examen"
        ASSIGNMENT = 'assignment', "Devoir"
        QUIZ = 'quiz', "Interrogation"
        
    class Method(models.TextChoices):
        ORAL = 'oral', "Orale"
        WRITTEN = 'written', "Ecrite"
        
    title = models.CharField(max_length=190, verbose_name="Titre de l'epreuve")
    course = models.ForeignKey(Course, on_delete=models.PROTECT, verbose_name="Cours")
    type = models.CharField(max_length=40, choices=Type.choices, verbose_name="Type d'epreuve")
    method = models.CharField(max_length=40, choices=Method.choices, verbose_name="Methode d'epreuve", default=Method.WRITTEN)
    max_points = models.IntegerField(default=0, verbose_name="Max points")
    class_average = models.FloatField(default=0.0, verbose_name="Moyenne de la classe")
    created_at = models.DateTimeField(auto_now_add=True)
    conducted_at = models.DateTimeField(verbose_name="L'heure de la passation du test", null=True, blank=True)
    due_date = models.DateField(verbose_name="Date de rendu", null=True, blank=True)
    
    class Meta:
        verbose_name = "Epreuve"
        ordering = ['-conducted_at', '-created_at']
        
        constraints = [
            models.CheckConstraint(
                condition= models.Q(type='exam') | models.Q(type='quiz') & models.Q(conducted_at__isnull=False),
                name='test_exam_needs_conducted_at'
            ),
            models.CheckConstraint(
                condition= models.Q(type='assignment') & models.Q(due_date__isnull=False),
                name='test_assignment_needs_due_date'
            )
        ]
        
    def __str__(self) -> str:
        return f"{self.type.lower()} de {self.course.name} : {self.title}"
    
class Grade(models.Model):
    enrollment = models.ForeignKey('students.Enrollment', on_delete=models.PROTECT, verbose_name="L'élève")
    test = models.ForeignKey(Test, on_delete=models.PROTECT, verbose_name="Epreuve")
    score = models.FloatField(default=0.0, verbose_name="Score de l'eleve")
    graded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Note"
        ordering = ['-graded_at']
        
    def __str__(self) -> str:
        return f"Note de l'eleve {self.enrollment.student} pour l'epreuve {self.test.title} : {self.score}"
