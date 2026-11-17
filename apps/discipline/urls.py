from django.urls import path
from .views import justify_student

app_name = 'discipline'
urlpatterns = [
    path('enrollment/<int:enrollment_id>/justify/', justify_student, name='justify_student'),
]
