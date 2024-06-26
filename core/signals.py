# signals.py
from django.core.files.base import ContentFile
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Trainer


@receiver(post_save, sender=Trainer)
def handle_uploaded_file(sender, instance, **kwargs):
    print("File saved")







