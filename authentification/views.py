from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User,Group
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from .forms import CaptchaForm,ProfileForm,ProfileEditForm,CustomPasswordChangeForm
from django.contrib.auth.hashers import make_password   
from django.db import transaction
from .models import OTP, Profile

from django.core.mail import send_mail
from django.conf import settings

from django.contrib.auth import update_session_auth_hash
from authentification.decorators import user_is_in_group
import pyotp
import qrcode
import io
import base64

# Create your views here.
def login_view(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')

        captchaForm = CaptchaForm(request.POST)
        if not captchaForm.is_valid():
            messages.error(request, "Captcha invalide.")
            return redirect("login")

        try:
            user_obj = User.objects.get(
                Q(username=username_or_email) |
                Q(email=username_or_email)
            )
            user = authenticate(
                request,
                username=user_obj.username,
                password=password
            )
        except User.DoesNotExist:
            user = None

        if user is not None:
            if not user.profile.active:
                messages.error(request, "Your account is inactive. Please contact your administrator.")
                return redirect("login")

            # ✅ Si 2FA activée pour email ou Google Authenticator
            if user.profile.use_2fa_email or user.profile.use_2fa_totp:
                # Création OTP email si activé
                if user.profile.use_2fa_email:
                    otp = OTP.objects.create(user=user)
                    user.email_user(
                        "Code de vérification",
                        f"Votre code de connexion est : {otp.code}"
                    )

                # On stocke l'id de l'utilisateur en session
                request.session['pre_2fa_user'] = user.id
                return redirect('verify_otp')

            else:
                # Pas de 2FA → login direct
                login(request, user)

                if user.groups.filter(name="reseller").exists():
                    return redirect('list_category')
                if user.groups.filter(name="admin").exists():
                    return redirect('list_user')
                return redirect('list')

        else:
            messages.error(request, "Identifiants invalides")
    else:
        captchaForm = CaptchaForm()

    return render(request, 'login.html', {'captchaForm': captchaForm})



def verify_otp(request):
    user_id = request.session.get('pre_2fa_user')
    if not user_id:
        messages.error(request, "Your session has expired or you are not logged in.")
        return render(request, "verify_otp.html")

    user = get_object_or_404(User, id=user_id)
    profile = user.profile

    if request.method == "POST":
        email_code = request.POST.get("otp")        # code email
        totp_code = request.POST.get("totp_code")   # code Google Auth

        # ✅ Vérification OTP Email si activé
        if profile.use_2fa_email:
            otp = OTP.objects.filter(user=user, code=email_code).last()
            if not otp or not otp.is_valid():
                messages.error(request, "Code email invalide ou expiré.")
                return render(request, "verify_otp.html")

        # ✅ Vérification TOTP Google Authenticator si activé
        if profile.use_2fa_totp:
            if not profile.totp_secret:
                messages.error(request, "Google Authenticator non configuré.")
                return render(request, "verify_otp.html")

            totp = pyotp.TOTP(profile.totp_secret)
            if not totp.verify(totp_code):
                messages.error(request, "Code Google Authenticator invalide.")
                return render(request, "verify_otp.html")

        # ✅ Tout est correct → login
        login(request, user)
        request.session.pop('pre_2fa_user', None)

        # redirection selon groupe
        if user.groups.filter(name="reseller").exists():
            return redirect('list_category')
        if user.groups.filter(name="admin").exists():
            return redirect('list_user')
        return redirect('list')
    
    context = {
    'profile': profile
}

    return render(request, "verify_otp.html",context)


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
    messages.success(request, "Successfully logged out.")
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

                    # 4️⃣ Envoi email à l’admin
                    send_mail(
                        subject="New User Registration on the Platform",
                        message=f"""
                    Hello Admin,

                    A new user has just registered on the platform. Please find the details below:

                    -----------------------------
                    User Information:
                    Full Name: {first_name} {last_name}
                    Username : {username}
                    Email    : {email}
                    -----------------------------

                    Please activate their account at your earliest convenience.

                    Best regards,
                    Your System
                        """,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[settings.ADMIN_NOTIFICATION_EMAIL],
                        fail_silently=False,
                    )

                    
                    return redirect('success')

            except Exception as e:
                messages.error(request, f"Erreur lors de l'inscription : {e}")
        else:
            messages.error(request, "The form is invalid. Please check the captcha and fields.")

    else:
        form = ProfileForm()

    context = {
        'form': form

    }    

    return render(request, 'register.html', context)








def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileEditForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            # Mise à jour User
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.save()

            # TOTP: si activé et pas déjà configuré, générer secret
            profile = form.save(commit=False)
            if profile.use_2fa_totp and not profile.totp_secret:
                profile.totp_secret = pyotp.random_base32()

            profile.save()
            messages.success(request, "Profile successfully updated.")
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=profile, user=request.user)

    # Si TOTP activé → générer QR code
    qr_code_base64 = None
    if profile.use_2fa_totp and profile.totp_secret:
        totp_uri = pyotp.totp.TOTP(profile.totp_secret).provisioning_uri(
            name=request.user.email,
            issuer_name="Panel.Digideel Platform"
        )
        qr = qrcode.make(totp_uri)
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

    context = {
        'form': form,
        'qr_code_base64': qr_code_base64,
        'profile': profile
    }

    return render(request, 'profile.html', context)

def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()  # sauvegarde le nouveau mot de passe
            update_session_auth_hash(request, user)  # garde l'utilisateur connecté
            messages.success(request, "Mot de passe mis à jour avec succès !")
            return redirect('profile')
        else:
            messages.error(request, "Erreur dans le formulaire, veuillez corriger les champs ci-dessous.")
    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'change_password.html', {'form': form})



def success (request):
    return render(request,'partials/success.html')




