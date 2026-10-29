from students.models import Enrollment, StudentGuardian
from finance.models import Fee, FeePayment
from discipline.models import Punishment
from .models import Parent

def get_enrollments_from_parent(parent: Parent) -> list[Enrollment]:
    """Returns a list of all enrollement for which the student has parent as a parent"""
    # Extrude all parent and students links 
    enrollements : list[Enrollment] = []
    student_links = StudentGuardian.objects.filter(parent=parent)
    for student_link in student_links:
        # Extrude the student
        student = student_link.student
        # Extrude the student enrollment
        enrollement = Enrollment.objects.get(student=student)
        enrollements.append(enrollement)
        
    return enrollements

def get_student_data_from_enrollment(enrollment : Enrollment) -> dict[str, object]:
    data : dict[str, object] = {}
    data["student_info"] = {
        "first_name": enrollment.student.first_name,
        "middle_name": enrollment.student.middle_name,
        "last_name": enrollment.student.last_name,
        "school_class": enrollment.school_class
    }
    data["payments"] = FeePayment.objects.filter(enrollment=enrollment)
    data["punishment"] = Punishment.objects.filter(enrollment=enrollment)
    data["fee"] = Fee.objects.filter(school_class=enrollment.school_class, academic_year=enrollment.academic_year)