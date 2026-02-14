from django.db.models import Sum
from .models import Profile

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


