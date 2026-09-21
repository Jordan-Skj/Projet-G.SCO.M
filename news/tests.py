from datetime import timedelta
from io import BytesIO
from tempfile import TemporaryDirectory
from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.utils import timezone
from .models import News


class NewsTests(TestCase):
    def test_original_content_and_visibility(self):
        self.assertEqual(News.objects.published().count(), 3)
        for url in ['/', '/news/', '/news/40-ans/', '/admin/login/']:
            self.assertEqual(self.client.get(url).status_code, 200)
        for title, published, date in [('Draft', False, timezone.now()), ('Future', True, timezone.now() + timedelta(days=1))]:
            article = News.objects.create(title=title, slug=title.lower(), summary='Summary', content='Body', is_published=published, published_at=date)
            self.assertEqual(self.client.get(article.get_absolute_url()).status_code, 404)
            self.assertNotContains(self.client.get('/news/'), f'<h3>{title}</h3>')

    def test_uploaded_image_and_admin(self):
        user = get_user_model().objects.create_superuser('editor', 'editor@example.com', 'test-password')
        self.client.force_login(user)
        self.assertEqual(self.client.get('/admin/news/news/').status_code, 200)
        self.assertEqual(self.client.get('/admin/news/news/add/').status_code, 200)
        with TemporaryDirectory() as directory, override_settings(MEDIA_ROOT=directory):
            data = BytesIO()
            Image.new('RGB', (20, 20)).save(data, format='PNG')
            article = News.objects.get(slug='40-ans')
            article.image = SimpleUploadedFile('test.png', data.getvalue(), content_type='image/png')
            article.save()
            for url in ['/', '/news/', article.get_absolute_url()]:
                self.assertContains(self.client.get(url), article.image.url)
