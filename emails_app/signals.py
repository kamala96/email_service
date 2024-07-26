from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from emails_app.models import Client, SMTPSettings
from emails_app.utils import generate_unique_api_key, set_smtp_settings


@receiver(post_save, sender=SMTPSettings)
def update_smtp_settings(sender, instance, created, **kwargs):
    """
    Signal receiver to update SMTP settings when SMTPSettings model is saved.
    """
    set_smtp_settings()


# @receiver(post_save, sender=Client)
# def create_user_for_client(sender, instance, created, **kwargs):
#     if created:
#         # Check if user already exists with the same static IP
#         existing_user = User.objects.filter(
#             username=f'client_{instance.static_ip.replace(".", "_")}').first()
#         if not existing_user:
#             # Create a new user with a username based on IP
#             user = User.objects.create_user(
#                 username=f'client_{instance.static_ip.replace(".", "_")}')
#             instance.user = user
#             instance.save()
#         else:
#             instance.user = existing_user
#             instance.save()


@receiver(pre_save, sender=Client)
def create_user_for_client(sender, instance, **kwargs):
    if not instance.user:
        # Check if user already exists with the same static IP
        existing_user = User.objects.filter(
            username=f'client_{instance.static_ip.replace(".", "_")}').first()
        if not existing_user:
            # Create a new user with a username based on IP
            user = User.objects.create_user(
                username=f'client_{instance.static_ip.replace(".", "_")}')
            instance.user = user
        else:
            instance.user = existing_user


@receiver(post_save, sender=Client)
def update_user_for_client(sender, instance, **kwargs):
    if instance.user:
        # Check if the static IP has changed
        old_instance = sender.objects.filter(pk=instance.pk).first()
        if old_instance and old_instance.static_ip != instance.static_ip:
            # Update the username if the static IP has changed
            new_username = f'client_{instance.static_ip.replace(".", "_")}'
            if instance.user.username != new_username:
                instance.user.username = new_username
                instance.user.save()
