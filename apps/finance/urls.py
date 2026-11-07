from django.urls import path
from .views import ask_exemption

app_name = 'finance'
urlpatterns = [
    path('enrollment/<int:enrollment_id>/ask-exemption/', ask_exemption, name='ask_exemption'),
]
