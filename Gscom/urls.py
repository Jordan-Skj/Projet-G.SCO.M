from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('home.urls')),
    path('admin/', admin.site.urls),
    path('press/', include('press.urls')),
    path('contact/', include('contact.urls')),
    path('account/', include('accounts.urls')),
    path('student/', include('students.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
