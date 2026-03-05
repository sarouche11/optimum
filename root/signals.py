from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Notification, ProductAchat, StatusAchat


@receiver(post_save, sender=User)
def notify_admin_new_user(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:

        admins = User.objects.filter(groups__name='admin')

        for admin in admins:
            Notification.objects.create(
                user=admin,
                message=f"Nouvelle inscription : {instance.username}"
            )


@receiver(post_save, sender=ProductAchat)
def notify_reseller_on_rejected(sender, instance, created, **kwargs):
    if created:
        return
    if instance.status != StatusAchat.REJECTED:
        return

    Notification.objects.create(
        user=instance.profil.user,
        message=f"Votre achat pour le produit '{instance.product.name}' a été rejeté et remboursé."
    )