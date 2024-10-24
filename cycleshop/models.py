from django.db import models
from django.contrib.auth.models import User
from products.models import Wishlist
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    """A model to store additional user profile information."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    wishlist = models.OneToOneField(Wishlist, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.user.username


class NewsletterSubscriber(models.Model):
    """Model to store newsletter subscribers."""
    email = models.EmailField(unique=True)
    date_subscribed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a Profile and Wishlist when a new User is created."""
    if created:
        profile = Profile.objects.create(user=instance)
        wishlist = Wishlist.objects.create(user=instance)
        profile.wishlist = wishlist
        profile.save()