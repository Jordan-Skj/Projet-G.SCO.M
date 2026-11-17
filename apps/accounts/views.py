from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model

from apps.accounts.services import create_parent_user
from apps.discipline.forms import JustificationForm
from apps.finance.forms import ExemptionForm, FeePaymentForm
from apps.students.models import Enrollment
from apps.students.forms import EnrollmentDocumentResubmissionForm, EnrollmentForm
from apps.studies.models import CourseSchedule, Grade

from .models import CustomUser, Parent
from .forms import ParentLoginForm, ParentSignUpForm
from .localisation import KINSHASA

User = get_user_model()

def parent_login(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect('account:parent_account')
    
    form = ParentLoginForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                if getattr(user, 'role', None) != CustomUser.Role.PARENT:
                    form.add_error(None, "Email ou mot de passe incorrect.")
                else:
                    login(request, user)
                    return redirect('account:parent_account')
            else:
                # Generic error to prevent email enumeration
                form.add_error(None, "Email ou mot de passe incorrect.")
                
    return render(request, 'accounts/parent_login.html', {'form': form})


def parent_sign_up(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect('account:parent_account')
    
    form = ParentSignUpForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():       
        print('Post and valid')     
        user = create_parent_user(form.cleaned_data)
        login(request, user)
        return redirect('account:parent_account')
        
    return render(request, 'accounts/sign_up.html', {'form': form, 'KINSHASA': KINSHASA})
    

@login_required
def parent_logout(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect('home:index')


@login_required
def parent_account(request: HttpRequest) -> HttpResponse:
    data = {}
    if getattr(request.user, 'role') == CustomUser.Role.PARENT:
        try:
            parent = Parent.objects.get(user=request.user)
            enrollments = (
                Enrollment.objects.filter(
                    student__guardian_links__parent=parent,
                    student__guardian_links__is_active=True,
                )
                .select_related('student', 'school_class', 'academic_year')
                .prefetch_related(
                    'fee_payments__fee',
                    'punishments',
                    'absences',
                    'latenesses',
                    'documents',
                )
                .order_by(
                    'student_id',
                    '-academic_year__is_current',
                    '-academic_year__start_date',
                )
                .distinct()
            )
            children_by_student = {}
            for enrollment in enrollments:
                child = children_by_student.get(enrollment.student_id)
                if child is None:
                    child = {
                        'student': enrollment.student,
                        'enrollment': enrollment,
                        'enrollment_history': [],
                    }
                    children_by_student[enrollment.student_id] = child
                child['enrollment_history'].append(enrollment)

            children = []
            for child in children_by_student.values():
                enrollment = child['enrollment']
                fees = list(
                    enrollment.school_class.fees.filter(
                        academic_year=enrollment.academic_year
                    )
                )
                fee_balances = [
                    {
                        'fee': fee,
                        'outstanding': fee.outstanding_for(enrollment),
                    }
                    for fee in fees
                ]
                can_manage = (
                    enrollment.academic_year.is_current
                    and enrollment.status == Enrollment.Status.ENROLLED
                )
                child.update({
                    'guardian_link': enrollment.student.guardian_links.filter(
                        parent=parent,
                        is_active=True,
                    ).first(),
                    'can_manage_enrollment': can_manage,
                    'can_pay_fees': (
                        can_manage
                        and any(balance['outstanding'] > 0 for balance in fee_balances)
                    ),
                    'payments': enrollment.fee_payments.all(),
                    'punishments': enrollment.punishments.all(),
                    'absences': enrollment.absences.all(),
                    'latenesses': enrollment.latenesses.all(),
                    'fee_balances': fee_balances,
                    'grades': Grade.objects.filter(enrollment=enrollment)
                    .select_related('test', 'test__course'),
                    'course_schedule': CourseSchedule.objects.filter(
                        course__school_class=enrollment.school_class
                    ).select_related('course'),
                    'documents': enrollment.documents.all(),
                    'exemptions': enrollment.exemptions.select_related('fee').all(),
                    'document_form': EnrollmentDocumentResubmissionForm(
                        enrollment=enrollment
                    ),
                    'exemption_form': ExemptionForm(enrollment=enrollment),
                    'justification_form': JustificationForm(enrollment=enrollment),
                    'fee_payment_form': FeePaymentForm(enrollment=enrollment),
                })
                children.append(child)

            data['children'] = children
            data['enrollment_form'] = EnrollmentForm()
            
            return render(request, 'accounts/parent_account.html', data)
        except Parent.DoesNotExist:
            return render(request, 'accounts/bad_auth.html', {'error': "Une erreur d'authentification est survenue. Veuillez réessayer."}, status=403)
    else:
        return render(request, 'accounts/bad_auth.html', {'error': "Une erreur d'authentification est survenue. Veuillez réessayer."}, status=403)
