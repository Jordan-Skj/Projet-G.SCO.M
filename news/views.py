from django.views.generic import DetailView, ListView
from .models import News


class NewsListView(ListView):
    template_name = 'news/list.html'
    context_object_name = 'articles'
    paginate_by = 9

    def get_queryset(self):
        return News.objects.published()


class NewsDetailView(DetailView):
    template_name = 'news/detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        return News.objects.published()
