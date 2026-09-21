import logging
from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from news.models import News
from .forms import ContactForm

logger = logging.getLogger(__name__)


@require_POST
def send(request):
    ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    form = ContactForm(request.POST)
    if not form.is_valid():
        if ajax:
            return JsonResponse({'success': False, 'message': 'Veuillez corriger les champs indiqués.', 'errors': form.errors.get_json_data()}, status=400)
        return render(request, 'home/index.html', {'form': form, 'articles': News.objects.published()[:3]}, status=400)
    data = form.cleaned_data
    subject = dict(form.fields['objet'].choices).get(data['objet']) if data['objet'] else 'Contact'
    try:
        sent = EmailMessage(
            subject=f'[G.SCO.M] {subject}',
            body=f"Nom : {data['name']}\nE-mail : {data['email']}\nObjet : {subject}\n\n{data['message']}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.CONTACT_EMAIL], reply_to=[data['email']],
        ).send(fail_silently=False)
        if sent != 1:
            raise RuntimeError('Email backend did not accept message')
    except Exception:
        logger.exception('Contact email delivery failed')
        message = 'L’envoi a échoué. Veuillez réessayer plus tard.'
        if ajax:
            return JsonResponse({'success': False, 'message': message}, status=503)
        form.add_error(None, message)
        return render(request, 'home/index.html', {'form': form, 'articles': News.objects.published()[:3]}, status=503)
    message = 'Votre message a été envoyé avec succès. Merci !'
    if ajax:
        return JsonResponse({'success': True, 'message': message})
    messages.success(request, message)
    return redirect(reverse('home:index') + '#contact')
