from django.contrib.auth.models import User
from .models import Notification, ProductAchat, StatusAchat
from authentification.decorators import user_is_in_group
from django.db.models.signals import post_save
from django.dispatch import receiver


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

def creer_notification_refund(purchase):
    """
    Crée des notifications pour le reseller quand une demande d'achat est rejetée
    et remboursée.
    """
    # 🔔 Vérifie que le statut est bien REJECTED
    if purchase.status != StatusAchat.REJECTED:
        return

    profil = purchase.profil
    user = profil.user  # le reseller
    product = purchase.product

    # 🔔 Notification pour le reseller
    Notification.objects.create(
        user=user,
        message=f"Votre achat pour le produit '{product.name}' a été rejeté et remboursé."
    )

    # 🔔 Notifications pour les admins
    admins = User.objects.filter(groups__name='admin').exclude(id=user.id)

    for admin in admins:
        Notification.objects.create(
            user=admin,
            message=(
                f"{user.first_name} {user.last_name} ({user.username}) "
                f"a été remboursé pour le produit '{product.name}' "
                f"rejeté et remboursé (Quantité : {purchase.quantity})."
            )
        )        



