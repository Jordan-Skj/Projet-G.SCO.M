from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model

from apps.accounts.services import create_parent_user
from apps.discipline.forms import JustificationForm
from apps.finance.forms import ExemptionForm, FeePaymentForm
from apps.students.models import Enrollment
from apps.students.forms import EnrollmentForm

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
                    academic_year__is_current=True,
                )
                .select_related('student', 'school_class', 'academic_year')
                .prefetch_related('fee_payments', 'punishments', 'absences', 'latenesses')
                .distinct()
            )
            children = []
            for enrollment in enrollments:
                children.append({
                    'enrollment': enrollment,
                    'payments': enrollment.fee_payments.all(),
                    'punishments': enrollment.punishments.all(),
                    'fees': enrollment.school_class.fees.filter(academic_year=enrollment.academic_year),
                    'tests': enrollment.grade.filter.all(),
                    'exemption_form': ExemptionForm(enrollment=enrollment),
                    'justification_form': JustificationForm(enrollment=enrollment),
                    'fee_paymment_form': FeePaymentForm(enrollment=enrollment),
                })

            data['children'] = children
            data['enrollment_form'] = EnrollmentForm()
            
            return render(request, 'accounts/parent_account.html', data)
        except Parent.DoesNotExist:
            return render(request, 'accounts/bad_auth.html', {'error': "Une erreur d'authentification est survenue. Veuillez réessayer."}, status=403)
    else:
        return render(request, 'accounts/bad_auth.html', {'error': "Une erreur d'authentification est survenue. Veuillez réessayer."}, status=403)
