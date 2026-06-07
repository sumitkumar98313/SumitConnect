from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile


# this signal fires every time a User object is saved
# if the user was just created, we create a Profile for them automatically
# this way we don't have to manually create profiles in views
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        # only create profile for brand new users, not on every save
        Profile.objects.create(user=instance)


# this signal makes sure the profile is also saved
# whenever the user object is saved
@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()
