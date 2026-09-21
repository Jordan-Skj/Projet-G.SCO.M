from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.templatetags.static import static


class NewsQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True, published_at__lte=timezone.now())


class News(models.Model):
    title = models.CharField('titre', max_length=250)
    slug = models.SlugField(unique=True, max_length=250)
    summary = models.TextField('résumé')
    content = models.TextField('contenu')
    image = models.ImageField(upload_to='news/%Y/%m/', blank=True)
    original_image = models.CharField('image du site original', max_length=255, blank=True, editable=False)
    image_alt = models.CharField('description de l’image', max_length=250, blank=True)
    category = models.CharField('catégorie', max_length=80, blank=True)
    display_order = models.PositiveIntegerField('ordre d’affichage', default=0)
    is_featured = models.BooleanField('à la une', default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField('date de publication', default=timezone.now)
    is_published = models.BooleanField('publié', default=False)
    objects = NewsQuerySet.as_manager()

    class Meta:
        verbose_name = 'actualité'
        verbose_name_plural = 'actualités'
        ordering = ['-is_featured', 'display_order', '-published_at', '-pk']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news:detail', kwargs={'slug': self.slug})

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return static(self.original_image or 'assets/image/eleve.png')
