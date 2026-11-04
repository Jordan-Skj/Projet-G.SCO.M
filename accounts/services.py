from typing import Any

from students.models import Enrollment, StudentGuardian
from finance.models import Fee, FeePayment
from discipline.models import Punishment, Absence, Justification
from studies.models import Course, Grade, Lesson, Test
from .models import Parent

def get_enrollments_from_parent(parent: Parent) -> list[Enrollment]:
    """Returns a list of all enrollment for which the student has parent as a parent"""
    # Extrude all parent and students links 
    enrollments : list[Enrollment] = []
    student_links = StudentGuardian.objects.filter(parent=parent)
    for student_link in student_links:
        # Extrude the student
        student = student_link.student
        # Extrude the student enrollment
        enrollment = Enrollment.objects.get(student=student)
        enrollments.append(enrollment)
        
    return enrollments

def get_student_data_from_enrollment(enrollment : Enrollment) -> dict[str, Any]:
    data : dict[str, Any] = {
        'student_info': {
            'first_name': enrollment.student.first_name,
            'middle_name': enrollment.student.middle_name,
            'last_name': enrollment.student.last_name,
            'school_class': enrollment.school_class
        }, 
        'finance': {
            'payments': FeePayment.objects.filter(enrollment=enrollment),
            'fees': Fee.objects.filter(school_class=enrollment.school_class, academic_year=enrollment.academic_year)
        },
        'discipline' : {
            'punishments': Punishment.objects.filter(enrollment=enrollment),
            'absences': Absence.objects.filter(enrollment=enrollment),
            'justifications': Justification.objects.filter(enrollment=enrollment),
        },
        'studies': {
            'courses': Course.objects.filter(
                school_class=enrollment.school_class,
            ),
        },
    }

    data['studies']['lessons'] = []
    for course in data['studies']['courses']:
        lessons = Lesson.objects.filter(course=course)
        data['studies']['lessons'].append(lessons)

    data['studies']['tests'] = []
    for course in data['studies']['courses']:
        tests = Test.objects.filter(course=course)
        data['studies']['tests'].append(tests)

    data['studies']['grades'] = []
    for test in data['studies']['tests']:
        grades = Grade.objects.filter(test=test)
        data['studies']['grades'].append(grades)

    return data
    
    