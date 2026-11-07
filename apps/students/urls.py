from django.urls import path
from .views import enroll_child, pay_enrollment_fee

app_name = "student"
urlpatterns = [
    path('enroll', enroll_child, name='enroll_child'),
    path('enrollment/<slug:slug>/pay/', pay_enrollment_fee, name='pay_enrollment_fee'),
]
