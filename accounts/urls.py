from django.urls import path
from .views import parent_login, parent_sign_up, parent_account, parent_logout

app_name = 'account'
urlpatterns = [
    path('login', parent_login, name="parent_login"),
    path('sign_up', parent_sign_up, name="parent_sign_up"),
    path('logout', parent_logout, name="parent_logout"),
    path('parent_account', parent_account, name="parent_account"),
]