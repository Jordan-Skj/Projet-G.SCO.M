from uuid import uuid4

from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.audit.models import Auditlog
from apps.audit.services import log_action
from .forms import ExemptionForm, FeePaymentForm
from .models import FeePayment
from .saspay import PaymentError, collect_fee_payment
from .services import get_exchange_rate
from apps.students.models import Enrollment


def _parent_owns_enrollment(request: HttpRequest, enrollment: Enrollment) -> bool:
    return enrollment.student.guardian_links.filter(
        parent__user=request.user,
        is_active=True,
    ).exists()


@require_POST
@login_required
def ask_exemption(request: HttpRequest, enrollment_id: int) -> JsonResponse:
    enrollment = get_object_or_404(
        Enrollment,
        pk=enrollment_id,
        academic_year__is_current=True,
    )
    if not _parent_owns_enrollment(request, enrollment):
        return JsonResponse({'success': False, 'message': "Action non autorisée."}, status=403)
    if enrollment.status != Enrollment.Status.ENROLLED:
        return JsonResponse(
            {
                'success': False,
                'message': (
                    "Le dossier de l'enfant doit être vérifié par l'école "
                    "avant de soumettre une demande."
                ),
            },
            status=409,
        )

    form = ExemptionForm(request.POST, enrollment=enrollment)

    if not form.is_valid():
        return JsonResponse({'success': False, 'message': "Veuillez corriger les champs indiqués.", 'errors': form.errors.get_json_data()}, status=400)

    exemption = form.save(commit=False)
    exemption.enrollement = enrollment
    exemption.save()

    # Log the action
    log_action(actor=request.user, action=Auditlog.Action.CREATE, target=exemption)

    return JsonResponse({'success': True, 'message': "Derogation soumis et encours approbation."}, status=200)


@require_POST
@login_required
def pay_fee(request: HttpRequest, enrollment_id: int) -> JsonResponse:
    enrollment = get_object_or_404(
        Enrollment.objects.select_related('student', 'school_class', 'academic_year'),
        pk=enrollment_id,
        academic_year__is_current=True,
    )
    if not _parent_owns_enrollment(request, enrollment):
        return JsonResponse(
            {'success': False, 'message': "Action non autorisée."},
            status=403,
        )
    if enrollment.status != Enrollment.Status.ENROLLED:
        return JsonResponse(
            {
                'success': False,
                'message': (
                    "Le dossier de l'enfant doit être vérifié par l'école "
                    "avant de pouvoir payer les frais."
                ),
            },
            status=409,
        )

    form = FeePaymentForm(request.POST, enrollment=enrollment)
    if not form.is_valid():
        return JsonResponse(
            {
                'success': False,
                'message': "Veuillez corriger les champs indiqués.",
                'errors': form.errors.get_json_data(),
            },
            status=400,
        )

    if not getattr(settings, 'SASPAY_API_TOKEN', '').strip():
        return JsonResponse(
            {'success': False, 'message': "Le paiement mobile est momentanément indisponible."},
            status=503,
        )

    fee = form.cleaned_data['fee']
    currency = form.cleaned_data['currency']
    exchange_rate = get_exchange_rate(currency, fee.currency)
    if exchange_rate is None:
        return JsonResponse(
            {
                'success': False,
                'message': "Le taux de conversion de cette devise n'est pas configuré.",
            },
            status=400,
        )

    payment_reference = f'GS-{uuid4().hex}'
    payment = FeePayment.objects.create(
        enrollment=enrollment,
        fee=fee,
        amount_paid=form.cleaned_data['amount'],
        payment_date=timezone.localdate(),
        payment_method=FeePayment.PaymentMethod.MOBILE_MONEY,
        payment_currency=currency,
        exchange_rate=exchange_rate,
        receipt_reference=payment_reference,
        submitted_by=request.user,
    )
    log_action(actor=request.user, action=Auditlog.Action.CREATE, target=payment)

    try:
        collect_fee_payment(
            form.cleaned_data,
            request.user,
            payment_reference=payment_reference,
        )
    except PaymentError as error:
        return JsonResponse(
            {
                'success': False,
                'message': (
                    f"{error} Référence : {payment_reference}. "
                    "Vérifiez le statut auprès du secrétariat avant de réessayer."
                ),
                'payment_reference': payment_reference,
                'status': payment.status,
            },
            status=502,
        )

    return JsonResponse(
        {
            'success': True,
            'message': (
                "Demande de paiement envoyée à SasaPay. "
                "Le paiement reste en attente de confirmation."
            ),
            'payment_reference': payment_reference,
            'status': payment.status,
        },
        status=202,
    )
