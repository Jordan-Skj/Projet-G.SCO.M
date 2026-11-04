from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_POST

from students.models import Enrollment, StudentGuardian
from .forms import ExemptionForm

@require_POST
@login_required(login_url='account/login')
def ask_exemption(request : HttpRequest) -> JsonResponse:
    enrollment = Enrollment.objects.get(
        student=StudentGuardian.objects.get(parent__user=request.user).student
    )
    form = ExemptionForm(request.POST, enrollment=enrollment)

    if not form.is_valid():
        return JsonResponse({'success': False, 'message': "Veuillez corriger les champs indiqués.", 'errors': form.errors.get_json_data()}, status=400)

    exemption = form.save(commit=False)
    exemption.enrollment = enrollment
    exemption.save()

    return JsonResponse({'success': True, 'message': "Derogation soumis et encours approbation ."}, status=200)

