from django.urls import path
from . import views

app_name = 'home'
urlpatterns = [
    path('', views.index, name='index'),
    path('notre-ecole/', views.ecole, name='ecole'),
    path('vie-scolaire/', views.vie_scolaire, name='vie_scolaire'),
    path('nous-contacter/', views.contact, name='contact'),
    path('formations/', views.formations, name='formations'),
    path('inscriptions/', views.inscriptions, name='inscriptions'),
]
