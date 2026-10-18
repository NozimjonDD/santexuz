from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.users.models import Consumer, User


@receiver(post_save, sender=User)
def create_consumer_profile(sender, instance, created, using, **kwargs):
    if created and instance.role == User.Role.CUSTOMER:
        Consumer.objects.using(using).get_or_create(user=instance)
