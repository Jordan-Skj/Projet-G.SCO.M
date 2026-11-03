from django.shortcuts import render
from news.models import News
from contact.forms import ContactForm

def index(request):
    return render(request, 'home/index.html', {'articles': News.objects.published()[:3]})


def inscriptions(request):
    return render(request, 'home/inscriptions.html')


def formations(request):
    return render(request, 'home/formations.html')


def school(request):
    return render(request, 'home/school.html')


def school_life(request):
    return render(request, 'home/school_life.html')


def contact(request):
    return render(request, 'home/contact.html', {'form': ContactForm()})
