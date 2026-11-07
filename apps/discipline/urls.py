from django.urls import path
from .views import justify_student

app_name = 'discipline'
urlpatterns = [
    path('enrollment/<slug:enrollment_slug>/justify/', justify_student, name='justify_student'),
]
