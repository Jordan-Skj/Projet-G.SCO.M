from django.shortcuts import render
from news.models import News
from contact.forms import ContactForm

def index(request):
    return render(request, 'home/index.html', {'articles': News.objects.published()[:3]})


def inscriptions(request):
    return render(request, 'home/inscriptions.html')


def formations(request):
    return render(request, 'home/formations.html')


def ecole(request):
    return render(request, 'home/ecole.html')


def vie_scolaire(request):
    return render(request, 'home/vie_scolaire.html')


def contact(request):
    return render(request, 'home/contact.html', {'form': ContactForm()})
