from django.db.models.fields import SlugField
from django.shortcuts import render
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_POST

from students.models import Enrollment
from .forms import JustificationForm

@require_POST
def justify_student(request: HttpRequest, slug: SlugField) -> JsonResponse:
    """Handles the justification of a student absence or lateness"""
    enrollment = Enrollment.objects.get(slug=slug)
    form = JustificationForm(request.POST, enrollment=enrollment)
    
    if form.is_valid():
        justification = form.save(commit=False)
        justification.enrollment = enrollment
        justification.save()
        return JsonResponse({'success': True, 'message': "Justification soumise avec succès"})
    else:
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
