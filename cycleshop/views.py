from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'cycleshop/home.html')


def contact(request):
    return render(request, 'cycleshop/contact.html')