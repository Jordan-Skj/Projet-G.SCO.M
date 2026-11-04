from django.urls import path
from .views import justify_student

app_name = 'discipline'
urlpatterns = [
    path('justify_student/<slug:slug>/', justify_student, name='justify_student'),
]
