from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

@receiver(pre_save, sender=User)
def ensure_unique_email(sender, instance, **kwargs):
    email = instance.email
    if User.objects.filter(email=email).exclude(pk=instance.pk).exists():
        raise ValidationError("Email must be unique.")