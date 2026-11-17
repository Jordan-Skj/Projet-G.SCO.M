from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from apps.audit.models import Auditlog
from apps.audit.services import log_action
from apps.students.models import Enrollment
from .forms import JustificationForm
from .models import Justification


@require_POST
@login_required
def justify_student(request: HttpRequest, enrollment_slug: str) -> JsonResponse:
    enrollment = get_object_or_404(Enrollment, slug=enrollment_slug, academic_year__is_current=True)
    if not enrollment.student.guardian_links.filter(parent__user=request.user, is_active=True).exists():
        return JsonResponse({'success': False, 'message': "Action non autorisée."}, status=403)

    form = JustificationForm(request.POST, enrollment=enrollment)
    if not form.is_valid():
        return JsonResponse(
            {'success': False, 'message': 'Veuillez corriger les champs indiqués.', 'errors': form.errors.get_json_data()},
            status=400,
        )

    justification = form.save(commit=False)
    justification.enrollment = enrollment
    justification.status = Justification.Status.PENDING
    if justification.type in ['uniform_violation', 'other', 'exemption']:
        justification.expired_at = date.today() + timedelta(days=14)
    justification.save()
    log_action(actor=request.user, action=Auditlog.Action.CREATE, target=justification)
    return JsonResponse({'success': True, 'message': "Justification soumise avec succès."})
