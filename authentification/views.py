from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User,Group
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from .forms import CaptchaForm,ProfileForm
from django.contrib.auth.hashers import make_password   
from django.db import transaction
from .models import OTP, Profile
import re
# Create your views here.



def login_view(request):

    if request.method == 'POST':

        username_or_email = request.POST.get('username')
        password = request.POST.get('password')

        print("=== TENTATIVE LOGIN ===")
        print("Identifiant saisi :", username_or_email)
        print("Mot de passe saisi :", password)

        captchaForm = CaptchaForm(request.POST)
        if not captchaForm.is_valid():
            print("❌ Captcha invalide")
            messages.error(request, "Captcha invalide.")
            return redirect("login")

        try:
            user_obj = User.objects.get(
                Q(username=username_or_email) |
                Q(email=username_or_email)
            )

            print("✅ Utilisateur trouvé :", user_obj.username)
            print("Email :", user_obj.email)
            print("Actif :", user_obj.is_active)

            user = authenticate(
                request,
                username=user_obj.username,
                password=password
            )
            print("Résultat authenticate :", user)

        except User.DoesNotExist:
            user = None

        if user is not None:

            # 👉 Création OTP
            otp = OTP.objects.create(user=user)

            # 👉 Envoi EMAIL
            user.email_user(
                "Code de vérification",
                f"Votre code de connexion est : {otp.code}"
            )

            # 👉 session temporaire
            request.session['pre_2fa_user'] = user.id

            return redirect('verify_otp')

        else:
            messages.error(request, "Identifiants invalides")

    else:
        captchaForm = CaptchaForm()

    context = {
            'captchaForm': captchaForm
    }    

    return render(request, 'login.html', context)


def verify_otp(request):

    user_id = request.session.get('pre_2fa_user')

    # ➜ Si pas de session : on reste propre
    if not user_id:
        messages.error(request, "Session expirée ou connexion non initiée.")
        return render(request, "verify_otp.html")

    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":

        code = request.POST.get("otp")

        otp = OTP.objects.filter(
            user=user,
            code=code
        ).last()

        if otp and otp.is_valid():

            login(request, user)

            # ➜ Suppression sécurisée SANS KeyError
            request.session.pop('pre_2fa_user', None)

            # 👉 redirection selon groupe
            if user.groups.filter(name="reseller").exists():
                return redirect('list_category')

            if user.groups.filter(name="admin").exists():
                return redirect('list_user')

            return redirect('list')

        # ➜ Ici on reste sur la page et on affiche juste le message
        messages.error(request, "Code invalide ou expiré")

    return render(request, "verify_otp.html")





def forbidden(request, code):
    code = str(code)

    if code == '403':
        err = "Accès non autorisé"
        detail = "Vous n'avez pas les permissions nécessaires pour accéder à cette page."
    elif code == '404':
        err = "Page non trouvée"
        detail = "La page que vous recherchez est introuvable."
    elif code == '500':
        err = "Erreur serveur"
        detail = "Une erreur interne s'est produite. Veuillez réessayer plus tard."
    elif code == '400':
        err = "Requête invalide"
        detail = "La requête ne peut pas être traitée. Vérifiez les informations envoyées."
    elif code == '401':
        err = "Non authentifié"
        detail = "Vous devez être connecté pour accéder à cette page."
    else:
        err = f"Erreur {code}"
        detail = "Une erreur inattendue s'est produite."

    context = {
        'code': code,
        'err': err,
        'detail': detail,

    }    

    return render(request, 'error.html', context)



def logout_view(request):
    storage = messages.get_messages(request)
    storage.used = True
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect ('login')


def register_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():

             
                    username = form.cleaned_data['username']
                    first_name = form.cleaned_data['first_name']
                    last_name = form.cleaned_data['last_name']
                    email = form.cleaned_data['email']
                    password = form.cleaned_data['password']

                    # 1️⃣ Création du User
                    user = User.objects.create(
                        username=username,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        password=make_password(password),
                          
                    )

                    # 2️⃣ Attribution automatique d’un groupe
                    group, created = Group.objects.get_or_create(name='reseller')
                    user.groups.add(group)

                    # 2️⃣ Création du Profile
                    profile = form.save(commit=False)
                    profile.user = user
                    profile.active = False
                    profile.save()

                    messages.success(
                        request,
                        "Votre compte a été créé ! Il sera activé par l'administrateur."
                    )
                    return redirect('success')

            except Exception as e:
                messages.error(request, f"Erreur lors de l'inscription : {e}")
        else:
            messages.error(request, "Le formulaire est invalide. Vérifiez le captcha et les champs.")

    else:
        form = ProfileForm()

    context = {
        'form': form

    }    

    return render(request, 'register.html', context)

def success (request):
    return render(request,'partials/success.html')