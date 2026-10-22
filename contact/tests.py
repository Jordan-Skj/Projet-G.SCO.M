from unittest.mock import patch
from django.core import mail
from django.test import Client, TestCase, override_settings


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ContactTests(TestCase):
    data = {'name': 'Test Parent', 'email': 'parent@example.com', 'objet': 'inscription', 'message': 'Bonjour, informations sur les inscriptions.'}
    headers = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}

    def test_send_and_validation(self):
        response = self.client.post('/contact/', self.data, **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].reply_to, ['parent@example.com'])
        self.assertEqual(self.client.post('/contact/', {}, **self.headers).status_code, 400)
        self.assertEqual(self.client.post('/contact/', {**self.data, 'objet': 'invalid'}, **self.headers).status_code, 400)
        self.assertEqual(self.client.get('/contact/').status_code, 405)

    def test_failure(self):
        with patch('contact.views.EmailMessage.send', side_effect=OSError('SMTP offline')), self.assertLogs('contact.views', level='ERROR'):
            response = self.client.post('/contact/', self.data, **self.headers)
        self.assertEqual(response.status_code, 503)
        self.assertFalse(response.json()['success'])

    def test_csrf_and_non_ajax(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post('/contact/', self.data).status_code, 403)
        client.get('/nous-contacter/')
        token = client.cookies['csrftoken'].value
        self.assertRedirects(client.post('/contact/', {**self.data, 'csrfmiddlewaretoken': token}), '/nous-contacter/#contact-feedback')
        response = self.client.post('/contact/', {'name': 'Retained'})
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, 'home/contact.html')
        self.assertContains(response, 'value="Retained"', status_code=400)

    def test_non_ajax_delivery_failure_preserves_form(self):
        with patch('contact.views.EmailMessage.send', side_effect=OSError('SMTP offline')), self.assertLogs('contact.views', level='ERROR'):
            response = self.client.post('/contact/', self.data)
        self.assertTemplateUsed(response, 'home/contact.html')
        self.assertContains(response, 'Test Parent', status_code=503)
        self.assertContains(response, 'L’envoi a échoué.', status_code=503)
