from uuid import uuid4

from django.contrib.auth.decorators import login_required
from django.http import FileResponse, HttpRequest, HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.views.decorators.http import require_POST

from apps.accounts.models import Parent
from apps.finance.forms import MobileMoneyPaymentForm
from apps.finance.models import Fee
from apps.finance.views import pay_fee
from .forms import EnrollmentDocumentResubmissionForm, EnrollmentForm
from .models import AcademicYear, Enrollment, EnrollmentDocument, Student, StudentGuardian
from apps.audit.models import Auditlog
from apps.audit.services import log_action


@require_POST
@login_required
def enroll_child(request: HttpRequest) -> JsonResponse:
    form = EnrollmentForm(request.POST, request.FILES)

    if not form.is_valid():
        return JsonResponse(
            {
                'success': False,
                'message': "Veuillez corriger les champs et joindre les deux pièces obligatoires.",
                'errors': form.errors.get_json_data(),
            },
            status=400,
        )

    try:
        parent_account = Parent.objects.get(user=request.user)
    except Parent.DoesNotExist:
        return JsonResponse(
            {'success': False, 'message': "Aucun profil parent n'est associé à ce compte."},
            status=403,
        )

    academic_year = AcademicYear.objects.filter(is_current=True).first()
    if academic_year is None:
        return JsonResponse(
            {'success': False, 'message': "Aucune année scolaire active n'est configurée."},
            status=409,
        )

    with transaction.atomic():
        student = Student.objects.create(
            admission_number=f"P-{uuid4().hex[:20]}",
            first_name=form.cleaned_data['first_name'],
            middle_name=form.cleaned_data['middle_name'],
            last_name=form.cleaned_data['last_name'],
            date_of_birth=form.cleaned_data['date_of_birth'],
            gender=form.cleaned_data['gender'],
        )
        guardian_link = StudentGuardian.objects.create(
            parent=parent_account,
            relationship=form.cleaned_data['relation'],
            student=student,
        )
        enrollment = Enrollment.objects.create(
            student=student,
            school_class=form.cleaned_data['school_class'],
            academic_year=academic_year,
        )
        for document_type in EnrollmentDocument.Type:
            document = EnrollmentDocument.objects.create(
                enrollment=enrollment,
                document_type=document_type,
                file=form.cleaned_data[document_type],
            )
            log_action(
                actor=request.user,
                action=Auditlog.Action.CREATE,
                target=document,
            )
        log_action(actor=request.user, action=Auditlog.Action.CREATE, target=student)
        log_action(actor=request.user, action=Auditlog.Action.CREATE, target=guardian_link)
        log_action(actor=request.user, action=Auditlog.Action.CREATE, target=enrollment)

    return JsonResponse(
        {
            'success': True,
            'message': (
                "Dossier envoyé. L'inscription restera en attente jusqu'à la "
                "vérification de l'acte de naissance et de la photo par l'école."
            ),
            'enrollment_id': enrollment.pk,
        },
        status=201,
    )


@require_POST
@login_required
def resubmit_enrollment_documents(
    request: HttpRequest,
    enrollment_id: int,
) -> JsonResponse:
    enrollment = get_object_or_404(
        Enrollment.objects.select_related('student'),
        pk=enrollment_id,
    )
    if not enrollment.student.guardian_links.filter(
        parent__user=request.user,
        is_active=True,
    ).exists():
        return JsonResponse({'success': False, 'message': "Action non autorisée."}, status=403)
    if enrollment.status != Enrollment.Status.PENDING:
        return JsonResponse(
            {'success': False, 'message': "Ce dossier n'est plus modifiable."},
            status=409,
        )

    form = EnrollmentDocumentResubmissionForm(
        request.POST,
        request.FILES,
        enrollment=enrollment,
    )
    if not form.documents_to_submit:
        return JsonResponse(
            {'success': False, 'message': "Aucune pièce ne nécessite une nouvelle soumission."},
            status=409,
        )
    if not form.is_valid():
        return JsonResponse(
            {
                'success': False,
                'message': "Veuillez téléverser à nouveau les pièces demandées.",
                'errors': form.errors.get_json_data(),
            },
            status=400,
        )

    with transaction.atomic():
        for document_type, document in form.documents_to_submit:
            if document is None:
                document = EnrollmentDocument(
                    enrollment=enrollment,
                    document_type=document_type,
                )
                document.file = form.cleaned_data[document_type]
                document.save()
            else:
                old_name = document.file.name
                storage = document.file.storage
                document.file = form.cleaned_data[document_type]
                document.status = EnrollmentDocument.Status.PENDING
                document.rejection_reason = ''
                document.reviewed_by = None
                document.reviewed_at = None
                document.save()
                transaction.on_commit(
                    lambda storage=storage, name=old_name: storage.delete(name)
                )
            log_action(
                actor=request.user,
                action=Auditlog.Action.UPDATE,
                target=document,
            )
        enrollment.approved_by = None
        enrollment.approved_at = None
        enrollment.status = Enrollment.Status.PENDING
        enrollment.save(update_fields=['approved_by', 'approved_at', 'status'])

    return JsonResponse(
        {
            'success': True,
            'message': "Les pièces corrigées ont été renvoyées pour vérification.",
        },
        status=200,
    )


@login_required
def download_enrollment_document(request: HttpRequest, document_id: int) -> HttpResponse:
    document = get_object_or_404(
        EnrollmentDocument.objects.select_related('enrollment__student'),
        pk=document_id,
    )
    is_parent = document.enrollment.student.guardian_links.filter(
        parent__user=request.user,
        is_active=True,
    ).exists()
    can_review_documents = (
        request.user.has_perm('students.view_enrollmentdocument')
        or request.user.has_perm('students.change_enrollmentdocument')
    )
    if not (can_review_documents or is_parent):
        return JsonResponse({'success': False, 'message': "Action non autorisée."}, status=403)

    response = FileResponse(
        document.file.open('rb'),
        as_attachment=True,
        filename=document.file.name.rsplit('/', 1)[-1],
        content_type='application/octet-stream',
    )
    response['X-Content-Type-Options'] = 'nosniff'
    response['Cache-Control'] = 'private, no-store'
    return response

@require_POST
@login_required
def pay_enrollment_fee(request: HttpRequest, enrollment_id: int) -> JsonResponse:
    form = MobileMoneyPaymentForm(request.POST)
    if not form.is_valid():
        return JsonResponse(
            {
                'success': False,
                'message': "Veuillez corriger les champs indiqués.",
                'errors': form.errors.get_json_data(),
            },
            status=400,
        )

    try:
        parent_account = Parent.objects.get(user=request.user)
    except Parent.DoesNotExist:
        return JsonResponse(
            {'success': False, 'message': "Action non autorisée."},
            status=403,
        )

    enrollment = get_object_or_404(
        Enrollment.objects.select_related('school_class', 'academic_year', 'student'),
        pk=enrollment_id,
    )
    if not enrollment.student.guardian_links.filter(
        parent=parent_account,
        is_active=True,
    ).exists():
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
                    "avant de pouvoir payer les frais d'inscription."
                ),
            },
            status=409,
        )

    fee = Fee.objects.filter(
        school_class=enrollment.school_class,
        academic_year=enrollment.academic_year,
        name__icontains="inscription",
    ).first()
    if fee is None:
        return JsonResponse(
            {'success': False, 'message': "Aucun frais d'inscription n'est défini pour cette classe."},
            status=404,
        )

    outstanding = fee.outstanding_for(enrollment)
    if outstanding <= 0:
        return JsonResponse(
            {'success': False, 'message': "Les frais d'inscription sont déjà réglés."},
            status=409,
        )

    payment_data = request.POST.copy()
    payment_data.update({
        'fee': str(fee.pk),
        'amount': str(outstanding),
        'currency': fee.currency,
    })
    request.POST = payment_data
    return pay_fee(request, enrollment.pk)
