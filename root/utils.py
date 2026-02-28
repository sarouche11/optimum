from django.contrib.auth.models import User
from .models import Notification
from authentification.decorators import user_is_in_group
from django.db.models.signals import post_save
from django.dispatch import receiver

@user_is_in_group('admin')
def creer_notification_request(purchase):
    """
    Crée des notifications pour une demande produit (REQUEST)
    """

    profil = purchase.profil
    user = profil.user
    product = purchase.product

    # 🔔 Notification pour le demandeur
    Notification.objects.create(
        user=user,
        message=f"Votre demande pour le produit '{product.name}' a été envoyée avec succès."
    )

    # 🔔 Notifications pour les admins
    admins = User.objects.filter(groups__name='admin').exclude(id=user.id)

    for admin in admins:
        Notification.objects.create(
            user=admin,
            message=(
                f"{user.first_name} {user.last_name} "
                f"a fait une demande pour le produit '{product.name}' "
                f"(Quantité : {purchase.quantity})."
            )
        ) 




@receiver(post_save, sender=User)
def create_notification_new_user(sender, instance, created, **kwargs):
    """
    Crée une notification quand un nouvel utilisateur s'inscrit
    """
    if created:  # uniquement à la création

        # 🔔 Notification pour l'utilisateur
        Notification.objects.create(
            user=instance,
            message="Votre compte a été créé avec succès. Bienvenue !"
        )

        # 🔔 Notification pour les admins
        admins = User.objects.filter(groups__name='admin').exclude(id=instance.id)

        for admin in admins:
            Notification.objects.create(
                user=admin,
                message=(
                    f"Nouvelle inscription : "
                    f"{instance.first_name} {instance.last_name} "
                    f"({instance.username}) vient de créer un compte."
                )
            )