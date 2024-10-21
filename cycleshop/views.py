from django.shortcuts import render, get_object_or_404, redirect
from .forms import ContactForm, UserForm, ProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile

# Create your views here.

def home(request):
    """A view to return the home page."""
    return render(request, 'cycleshop/home.html')


def contact(request):
    """A view to handle the contact form submission and display the contact page."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            
            return render(request, 'cycleshop/contact.html')
    else:
        form = ContactForm()

    return render(request, 'cycleshop/contact.html', {'form': form})


def search_request(request):
    """A view to handle search queries and return search results."""
    query = request.GET.get('q')
    
    products = Product.objects.filter(name__icontains=query)
    return render(request, 'products/search_results.html', {'products': products, 'query': query})


@login_required
def view_profile(request):
    """View to display the user's profile."""
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'profile/view_profile.html', {'profile': profile})


@login_required
def edit_profile(request):
    """View to allow users to edit their profile."""
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('view_profile')
            messages.error(request, 'Please correct the error below.')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)

    return render(request, 'profile/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required
def delete_profile(request):
    """View to delete the user's profile."""
    if request.method == 'POST':
        request.user.delete()
        messages.success(request, 'Your profile has been deleted successfully.')
        return redirect('home')

    return render(request, 'profile/delete_profile.html')