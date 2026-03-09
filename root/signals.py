from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Notification, ProductAchat, StatusAchat


print('signal lus')

@receiver(post_save, sender=User)
def notify_admin_new_user(sender, instance, created, **kwargs):
    print("Signal User déclenché !", created, instance.username)
    if created :
        admins = User.objects.filter(groups__name='admin')
        for admin in admins:
            Notification.objects.create(
                user=admin,
                message=f"👤 Nouvelle inscription : {instance.username}"
            )


# @receiver(post_save, sender=ProductAchat)
# def notify_reseller_on_rejected(sender, instance, created, **kwargs):
#     if created:
#         return
#     if instance.status != StatusAchat.REJECTED:
#         return

#     Notification.objects.create(
#         user=instance.profil.user,
#         message = f'<i class="fa fa-exclamation-triangle"></i> <strong>Rejected</strong><br/> Your purchase for the product "{instance.product.name}" has been rejected and refunded.'
#     )