from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404

from apps.audit.models import Auditlog
from apps.audit.services import log_action
from .forms import ExemptionForm
from apps.students.models import Enrollment


def _parent_owns_enrollment(request: HttpRequest, enrollment: Enrollment) -> bool:
    return enrollment.student.guardian_links.filter(parent__user=request.user, is_active=True).exists()

@require_POST
@login_required(login_url='account/login')
def ask_exemption(request : HttpRequest, enrollment_id: int) -> JsonResponse:
    enrollment = get_object_or_404(Enrollment, pk=enrollment_id, academic_year__is_current=True)
    if not _parent_owns_enrollment(request, enrollment):
        return JsonResponse({'success': False, 'message': "Action non autorisée."}, status=403)

    form = ExemptionForm(request.POST, enrollment=enrollment)

    if not form.is_valid():
        return JsonResponse({'success': False, 'message': "Veuillez corriger les champs indiqués.", 'errors': form.errors.get_json_data()}, status=400)

    exemption = form.save(commit=False)
    exemption.enrollement = enrollment
    exemption.save()

    # Log the action
    log_action(actor=request.user, action=Auditlog.Action.CREATE, target=exemption)

    return JsonResponse({'success': True, 'message': "Derogation soumis et encours approbation."}, status=200)
