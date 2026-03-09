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
       message = f'<i class="fa fa-check-circle" style="color: #20b093;"></i> Your request for the product "{product.name}" has been <span style="color:#20b093;"><strong>sent successfully</strong></span>.'
    )

    # 🔔 Notifications pour les admins
    admins = User.objects.filter(groups__name='admin').exclude(id=user.id)

    for admin in admins:
        Notification.objects.create(
            user=admin,
           message = (
                f'<i class="fa fa-check-circle" style="color:#20b093;"></i> '
                f'Your request for the product "{product.name}" has been <span style="color:#20b093;"><strong>sent successfully</strong></span>.'
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
        message=f'<i class="fa fa-exclamation-triangle" style="color:#ffbc34;"></i> <strong style="color:#cb1b1b;">Rejected</strong><br/> Your purchase for the product "{product.name}" has been rejected and refunded.'
    )


    

    # 🔔 Notifications pour les admins
    admins = User.objects.filter(groups__name='admin').exclude(id=user.id)

    for admin in admins:
        Notification.objects.create(
            user=admin,
            message = (
                f'<i class="fa fa-exclamation-triangle" style="color:#ffbc34;"></i> '
                f'<strong> {user.username} </strong><br/>'
                f'<span style="color:red"><strong>Rejected and refunded</strong></span> '
                f'for the product "{product.name}" (Quantity: {purchase.quantity}).'
            )
        )        



