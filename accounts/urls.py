from django.urls import path
from .views import parent_login, parent_sign_up, parent_account

app_name = 'account'
urlpatterns = [
    path('login', parent_login, name="parent_login"),
    path('sign_up', parent_sign_up, name="parent_sign_up"),
    path('parent_account', parent_login, name="parent_account"),
    
]