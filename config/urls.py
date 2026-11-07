from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('apps.home.urls')),
    path('admin/', admin.site.urls),
    path('press/', include('apps.press.urls')),
    path('contact/', include('apps.contact.urls')),
    path('account/', include('apps.accounts.urls')),
    path('student/', include('apps.students.urls')),
    path('finance/', include('apps.finance.urls')),
    path('discipline/', include('apps.discipline.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
