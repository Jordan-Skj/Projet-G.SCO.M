from django.contrib import admin
from django import forms
from django.db import transaction
from django.utils import timezone
from django.urls import reverse
from django.utils.html import format_html

from apps.audit.models import Auditlog
from apps.audit.services import log_action
from .models import (
    ENROLLMENT_REQUIRED_DOCUMENT_TYPES,
    Enrollment,
    EnrollmentDocument,
)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'school_class',
        'academic_year',
        'status',
        'approved_at',
    )
    list_filter = ('status', 'academic_year', 'school_class')
    search_fields = (
        'student__first_name',
        'student__last_name',
        'student__admission_number',
    )
    readonly_fields = (
        'student',
        'academic_year',
        'school_class',
        'status',
        'payment_status',
        'approved_by',
        'approved_at',
        'enrollment_date',
    )

    def has_add_permission(self, request) -> bool:
        return False


class EnrollmentDocumentReviewForm(forms.ModelForm):
    class Meta:
        model = EnrollmentDocument
        fields = ('status', 'rejection_reason')

    def clean(self):
        cleaned_data = super().clean()
        if (
            cleaned_data.get('status') == EnrollmentDocument.Status.REJECTED
            and not cleaned_data.get('rejection_reason', '').strip()
        ):
            self.add_error(
                'rejection_reason',
                "Indiquez les corrections attendues pour cette pièce.",
            )
        return cleaned_data


@admin.register(EnrollmentDocument)
class EnrollmentDocumentAdmin(admin.ModelAdmin):
    form = EnrollmentDocumentReviewForm
    list_display = (
        'enrollment',
        'document_type',
        'status',
        'submitted_at',
        'reviewed_by',
        'reviewed_at',
    )
    list_filter = ('status', 'document_type', 'enrollment__academic_year')
    search_fields = (
        'enrollment__student__first_name',
        'enrollment__student__last_name',
        'enrollment__student__admission_number',
    )
    readonly_fields = (
        'enrollment',
        'document_type',
        'file_download',
        'submitted_at',
        'reviewed_by',
        'reviewed_at',
    )
    fields = (
        'enrollment',
        'document_type',
        'file_download',
        'status',
        'rejection_reason',
        'submitted_at',
        'reviewed_by',
        'reviewed_at',
    )

    @admin.display(description="Fichier privé")
    def file_download(self, obj: EnrollmentDocument):
        url = reverse(
            'student:download_enrollment_document',
            kwargs={'document_id': obj.pk},
        )
        return format_html('<a href="{}">Télécharger la pièce</a>', url)

    def has_add_permission(self, request) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False

    @transaction.atomic
    def save_model(self, request, obj, form, change) -> None:
        enrollment = obj.enrollment
        previous_status = enrollment.status
        if obj.status == EnrollmentDocument.Status.PENDING:
            obj.reviewed_by = None
            obj.reviewed_at = None
        else:
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()
            if obj.status == EnrollmentDocument.Status.APPROVED:
                obj.rejection_reason = ''

        super().save_model(request, obj, form, change)
        log_action(
            actor=request.user,
            action=Auditlog.Action.UPDATE,
            target=obj,
        )

        documents_by_type = dict(
            enrollment.documents.values_list('document_type', 'status')
        )
        if all(
            documents_by_type.get(document_type) == EnrollmentDocument.Status.APPROVED
            for document_type in ENROLLMENT_REQUIRED_DOCUMENT_TYPES
        ):
            enrollment.status = Enrollment.Status.ENROLLED
            enrollment.approved_by = request.user
            enrollment.approved_at = timezone.now()
        else:
            enrollment.status = Enrollment.Status.PENDING
            enrollment.approved_by = None
            enrollment.approved_at = None
        enrollment.save(update_fields=['status', 'approved_by', 'approved_at'])
        if enrollment.status != previous_status:
            log_action(
                actor=request.user,
                action=Auditlog.Action.UPDATE,
                target=enrollment,
                before={'status': previous_status},
                after={'status': enrollment.status},
            )
