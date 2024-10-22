from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    """A model to store additional user profile information."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username


class NewsletterSubscriber(models.Model):
    """Model to store newsletter subscribers."""
    email = models.EmailField(unique=True)
    date_subscribed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email