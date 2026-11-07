from datetime import date
from django.contrib.auth.decorators import login_required
from django.forms.fields import SlugField
from django.http import HttpRequest, HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import render
from django.db import transaction
from django.views.decorators.http import require_POST

from apps.accounts.models import Parent
from apps.finance.forms import MobileMoneyPaymentForm
from apps.finance.models import Fee
from apps.finance.services import soft_money_money_pay
from .forms import EnrollmentForm
from .models import AcademicYear, Enrollment, Student, StudentGuardian
from apps.audit.models import Auditlog
from apps.audit.services import log_action


@require_POST
@login_required
def enroll_child(request : HttpRequest) -> JsonResponse | HttpResponse:
    form = EnrollmentForm(request.POST, request.FILES)

    if form.is_valid():
        first_name = form.cleaned_data['first_name']
        middle_name = form.cleaned_data['middle_name']
        last_name = form.cleaned_data['last_name']
        image = form.cleaned_data.get('profile_img')
        school_class = form.cleaned_data['school_class']
        relation = form.cleaned_data['relation']

        try:
            parent_account = Parent.objects.get(user=request.user)
        except Parent.DoesNotExist:
            return render(request, 'bad_request.html', {'success' : False, 'message' : "Action non permise."}, status=503)


        academic_year = AcademicYear.objects.filter(is_current=True).first()
        if academic_year is None:
            return JsonResponse({'success': False, 'message': "Aucune année scolaire active n'est configurée."}, status=409)

        with transaction.atomic():
            student = Student.objects.create(
                admission_number=f"PENDING-{parent_account.pk}-{Student.objects.count() + 1}",
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                date_of_birth=form.cleaned_data['date_of_birth'],
                gender=form.cleaned_data['gender'],
                profile_img=image,
            )
            guardian_link = StudentGuardian.objects.create(parent=parent_account, relationship=relation, student=student)
            enrollment = Enrollment.objects.create(student=student, school_class=school_class, academic_year=academic_year)
            log_action(actor=request.user, action=Auditlog.Action.CREATE, target=student)
            log_action(actor=request.user, action=Auditlog.Action.CREATE, target=guardian_link)
            log_action(actor=request.user, action=Auditlog.Action.CREATE, target=enrollment)

        return JsonResponse({'success': True, 'message': "Inscription soumise avec succès, en attente de paiement."}, status=200)
    else:
        return JsonResponse({'success' : False, 'message' : "Veuillez corriger les champs suivants:", 'errors' : form.errors.get_json_data()}, status=400)

@require_POST
@login_required
def pay_enrollment_fee(request : HttpRequest, slug : SlugField) -> JsonResponse | HttpResponse:
    form = MobileMoneyPaymentForm(request.POST)

    try:
        parent_account = Parent.objects.get(user=request.user)
        enrollment = Enrollment.objects.get(payment_status=Enrollment.PaymentStatus.UNPAID, slug=slug)
    except Parent.DoesNotExist:
        return render(request, 'bad_request.hml.html', {'message': "Action non permise."})
    except Enrollment.DoesNotExist:
        if Enrollment.objects.filter(slug=slug).exists():
            return JsonResponse({'success': False, 'message': "L'inscription a déjà été payée"}, status=503)

        return JsonResponse({'success': False, 'message': "Aucune inscription ne correspond à votre recherche."}, status=404)

    if form.is_valid():
        fee = Fee.objects.filter(
            school_class=enrollment.school_class,
            name__contains="Inscription",
        ).first()
        if fee is None:
            return JsonResponse(
                {'success': False, 'message': "Aucun frais d'inscription ne correspond à cette classe."},
                status=404,
            )

        amount_due = fee.amount
        phone_number = int(
            form.cleaned_data['phone_number']
        )
        operator = form.cleaned_data['operator']
        soft_money_money_pay(amount_due, phone_number, operator)

    enrollment.payment_status = Enrollment.PaymentStatus.PAID
    enrollment.save(update_fields=['payment_status'])
    log_action(actor=request.user, action=Auditlog.Action.UPDATE, target=enrollment, after={'payment_status': enrollment.payment_status})

    return JsonResponse({'success': True, 'message': "Inscription payée avec succès."}, status=200)
