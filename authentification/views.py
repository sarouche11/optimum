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
from .models import LoginHistory
from root.utils import get_browser,get_client_ip
from django.core.paginator import Paginator
import  secrets
import time
from .utils import logout_other_sessions





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

                ip = get_client_ip(request)
                browser = get_browser(request)
                LoginHistory.objects.create(
                        user=user,
                        ip_address=ip,
                        browser=browser,
                        user_agent=request.META.get('HTTP_USER_AGENT', '')
                    )

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
        form = CaptchaForm()
        return render(request, "login.html", {"form": form})

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
                return redirect('login')

        # ✅ Vérification TOTP Google Authenticator si activé
        if profile.use_2fa_totp:
            if not profile.totp_secret:
                messages.error(request, "Google Authenticator non configuré.")
                return redirect('login')

            totp = pyotp.TOTP(profile.totp_secret)
            if not totp.verify(totp_code):
                messages.error(request, "Code Google Authenticator invalide.")
                return redirect('login')

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



@user_is_in_group('admin', 'reseller')
def history_login(request):
    #-------------------  search -----------
    search = request.GET.get('search', '')

    #----------------- récupération du per_page --------
    per_page = request.GET.get('per_page', 10) 
    try:
        per_page = int(per_page)
    except:
        per_page = 10

    
    history_login = LoginHistory.objects.filter(user=request.user).order_by('timestamp')


    # -----------------------------------------
    if search:
        history_login = history_login.filter(
           Q(timestamp__icontains=search)
        )

    

    # ---------------Récupérer tous les paramètres GET sauf 'page' ------------
    params = request.GET.copy()
    if 'page' in params:
        params.pop('page')

    # ------------------Convertir en string utilisable dans les URLs-----------------
    querystring = params.urlencode() 

   
    paginator = Paginator(history_login, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number) 
    
    

    context = {
       'page_obj': page_obj,
       'search': search,
       'querystring': querystring,
       'per_page': per_page,
    }
    return render(request,'history_login.html',context)





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

    if request.method == "POST":

        form = CustomPasswordChangeForm(user=request.user, data=request.POST)

        if form.is_valid():

            otp = str(secrets.randbelow(900000) + 100000)

            request.session["otp"] = otp
            request.session["otp_expiry"] = time.time() + 300
            request.session["form_data"] = request.POST.dict()

            send_mail(
                "Code de vérification",
                f"Votre code est : {otp}",
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
            )

            return redirect("verify_otp_change_psw")

        return render(request, "change_password.html", {"form": form})

    form = CustomPasswordChangeForm(user=request.user)

    return render(request, "change_password.html", {"form": form})




def verify_otp_change_psw(request):

    if request.method == "POST":

        code = request.POST.get("otp")
        stored = request.session.get("otp")
        expiry = request.session.get("otp_expiry")

        if not stored or time.time() > expiry:
            messages.error(request, "Code expiré")
            return redirect("change_password")

        if code != stored:
            messages.error(request, "Code incorrect")
            return render(request, "verify_otp_psw.html")

        # restore form data
        form = CustomPasswordChangeForm(
            user=request.user,
            data=request.session.get("form_data")
        )

        if form.is_valid():
            user = form.save()

            update_session_auth_hash(request, user)

            # logout other devices
            logout_other_sessions(request, user)

            # cleanup
            request.session.flush()

            messages.success(request, "Mot de passe changé avec succès")
            return redirect("login")

    return render(request, "verify_otp_psw.html")





def success (request):
    return render(request,'partials/success.html')




