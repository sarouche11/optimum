from django.contrib.auth.models import User
from .models import Notification, ProductAchat, StatusAchat
from authentification.decorators import user_is_in_group
from django.db.models.signals import post_save
from django.dispatch import receiver
from cryptography.fernet import Fernet
from django.conf import settings
from user_agents import parse


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
          message=(
            f'<i class="bi bi-send" style="color:#20b093;"></i> '
            f'<strong>Request</strong><br/>'
            f'The user "{user.username}" has submitted a request for the product '
            f'"{product.name}".'
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
                f'<strong style="color:#cb1b1b;">Rejected </strong><br/>'
                f'The purchase by <strong>{user.username}</strong> for the product '
                f'"{product.name}" has been rejected and refunded.'
            )
        )       


cipher = Fernet(settings.ACTIVATION_CODE_KEY)

def encrypt_code(code):
    return cipher.encrypt(code.encode()).decode()

def decrypt_code(encrypted_code):
    return cipher.decrypt(encrypted_code.encode()).decode()         



def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_browser(request):
    ua_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(ua_string)
    # Retourne navigateur + OS
    return f"{user_agent.browser.family} - {user_agent.os.family}"



