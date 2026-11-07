from django.urls import path
from . import views

app_name = 'home'
urlpatterns = [
    path('', views.index, name='index'),
    path('our-school/', views.school, name='school'),
    path('school-life/', views.school_life, name='school_life'),
    path('contact/', views.contact, name='contact'),
    path('formations/', views.formations, name='formations'),
    path('enrollments/', views.inscriptions, name='inscriptions'),
]
