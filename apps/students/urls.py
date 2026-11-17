from django.urls import path
from .views import (
    download_enrollment_document,
    enroll_child,
    pay_enrollment_fee,
    resubmit_enrollment_documents,
)

app_name = "student"
urlpatterns = [
    path('enroll', enroll_child, name='enroll_child'),
    path(
        'enrollment/<int:enrollment_id>/documents/resubmit/',
        resubmit_enrollment_documents,
        name='resubmit_enrollment_documents',
    ),
    path(
        'documents/<int:document_id>/download/',
        download_enrollment_document,
        name='download_enrollment_document',
    ),
    path(
        'enrollment/<int:enrollment_id>/pay/',
        pay_enrollment_fee,
        name='pay_enrollment_fee',
    ),
]
