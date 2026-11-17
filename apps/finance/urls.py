from django.urls import path
from .views import ask_exemption, pay_fee

app_name = 'finance'
urlpatterns = [
    path('enrollment/<int:enrollment_id>/ask-exemption/', ask_exemption, name='ask_exemption'),
    path('enrollment/<int:enrollment_id>/pay/', pay_fee, name='pay_fee'),
]
