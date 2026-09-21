from django.shortcuts import render
from news.models import News
from contact.forms import ContactForm

def index(request):
    return render(request, 'home/index.html', {'articles': News.objects.published()[:3], 'form': ContactForm()})
