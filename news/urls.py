from django.urls import path
from .views import NewsListView, NewsDetailView

app_name = 'news'
urlpatterns = [
    path('<slug:slug>/', NewsDetailView.as_view(), name='detail')
]
