from datetime import datetime
from django.db import migrations


ARTICLES = [{'title': "GSCOM célèbre 40 ans d'excellence éducative", 'slug': '40-ans', 'summary': 'Le Groupe Scolaire de Mont-Ngafula a célébré son 40e anniversaire avec une cérémonie réunissant élèves, enseignants, anciens élèves et partenaires. Depuis 1986, GSCOM forme des leaders dans un environnement rigoureux et épanouissant.', 'content': 'Le Groupe Scolaire de Mont-Ngafula a célébré son 40e anniversaire avec une cérémonie réunissant élèves, enseignants, anciens élèves et partenaires. Depuis 1986, GSCOM forme des leaders dans un environnement rigoureux et épanouissant.', 'original_image': 'assets/image/eleve.png', 'image_alt': 'Cérémonie du 40e anniversaire du G.SCO.M', 'category': 'Événement', 'is_featured': True, 'is_published': True, 'published_at': '2025-05-12T12:00:00+01:00', 'display_order': 0}, {'title': 'Nouveau programme de bourses pour les étudiants méritants', 'slug': 'bourses', 'summary': 'GSCOM soutient les élèves à potentiel exceptionnel grâce à un programme de bourses inédit.', 'content': 'GSCOM soutient les élèves à potentiel exceptionnel grâce à un programme de bourses inédit.', 'original_image': 'assets/image/eleve.png', 'image_alt': 'Programme de bourses GSCOM', 'category': 'Programme', 'is_featured': False, 'is_published': True, 'published_at': '2025-04-03T12:00:00+01:00', 'display_order': 1}, {'title': 'Rentrée scolaire 2025–2026 : informations pratiques', 'slug': 'rentree-2025', 'summary': "Dates, documents à fournir et procédures d'inscription pour la nouvelle année scolaire.", 'content': "Dates, documents à fournir et procédures d'inscription pour la nouvelle année scolaire.", 'original_image': 'assets/image/extérieur_ecole.png', 'image_alt': 'Rentrée scolaire 2025-2026 au G.SCO.M', 'category': 'Rentrée', 'is_featured': False, 'is_published': True, 'published_at': '2025-08-20T12:00:00+01:00', 'display_order': 2}]

def seed(apps, schema_editor):
    News = apps.get_model('news', 'News')
    for record in ARTICLES:
        fields = dict(record)
        fields['published_at'] = datetime.fromisoformat(fields['published_at'])
        slug = fields.pop('slug')
        News.objects.using(schema_editor.connection.alias).get_or_create(slug=slug, defaults=fields)


class Migration(migrations.Migration):
    dependencies = [('news', '0002_alter_news_options_news_display_order')]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
