from django.db.models import Sum
from .models import Profile
from root.models import Notification

def solde_revendeur(request):
    if request.user.is_authenticated:
        try:
            profil = request.user.profile
            solde = profil.paiements.filter(active=True).aggregate(total=Sum('montant'))['total'] or 0
        except Profile.DoesNotExist:
            solde = 0
    else:
        solde = 0
    return {
        'solde_revendeur': solde
    }





def get_notifications(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    else:
        notifications = []
    print(any(not notif.is_read for notif in notifications))
    return {
        'notifications': notifications,
        'has_unread': any(not notif.is_read for notif in notifications)
    }