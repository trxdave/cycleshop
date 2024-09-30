from django.shortcuts import render
from .forms import ContactForm
from . import views

# Create your views here.

def home(request):
    """ A view to return the home page """
    
    return render(request, 'cycleshop/home.html')


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():

            return render(request, 'cycleshop/contact.html')
    else:
        form = ContactForm()

    return render(request, 'cycleshop/contact.html', {'form': form})


