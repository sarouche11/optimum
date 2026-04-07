from django.shortcuts import render
from authentification.decorators import user_is_in_group
from authentification.models import Profile
from .models import (Category,SubCategory,Product,ActivationCode,Paiement,
                     ProductAchat,PurchaseCode,CatgoryType,StatusAchat,ProductType,Notification,ActivationCodeLog)
from .forms import (CategoryForm, SubCategoryForm, 
                    ProductForm, ActivationCodeForm,EditActivationCodeForm,ProductRequestUpdateForm,
                    UserCategoryForm)
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from decimal import Decimal
from django.db.models import Sum
from django.utils import timezone
from django.http import JsonResponse
from django.db import transaction

from django.core.mail import send_mail
from django.conf import settings

from .utils import creer_notification_request,creer_notification_refund
from django.views.decorators.http import require_POST
from .context_processors import get_notifications
from django.contrib.auth.decorators import login_required
import os
from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage

from authentification.models import Profile
from django.contrib.auth.decorators import user_passes_test

from django.http import HttpResponseForbidden
from user_agents import parse
from authentification.forms import AddProfileForm
from django.contrib.auth.models import User,Group
from django.contrib.auth.hashers import make_password 

from .utils import encrypt_code
import hashlib, secrets

from .utils import decrypt_code
from django.urls import reverse
import pyotp
import qrcode
import io
import base64
from authentification.models import Profile
import time
# ================================== adminn decryptage =====



@user_is_in_group('admin')  
def reveal_activation_code(request, code_id):

    # 🔐 Vérification accès staff
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect(reverse('forbidden', kwargs={'code': 403}))

    code_obj = get_object_or_404(ActivationCode, id=code_id)

    real_code = None
    error_msg = None

    # =========================================================
    # 1️⃣ Génération mot de passe temporaire (expire 60s)
    # =========================================================
    regenerate_password = False
    expiry = request.session.get('admin_decrypt_expiry', 0)

    if 'admin_decrypt_hash' not in request.session or time.time() > expiry:
        regenerate_password = True

    if regenerate_password:
        temp_password = secrets.token_urlsafe(10)
        temp_password_hash = hashlib.sha256(temp_password.encode()).hexdigest()

        request.session['admin_decrypt_hash'] = temp_password_hash
        request.session['admin_decrypt_expiry'] = time.time() + 60

        send_mail(
            subject="Mot de passe temporaire",
            message=f"Votre mot de passe (valide 60s) : {temp_password}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
            fail_silently=False,
        )

    # =========================================================
    # 2️⃣ Vérification POST
    # =========================================================
    if request.method == "POST":

        password = request.POST.get("admin_password", "")
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        expiry = request.session.get('admin_decrypt_expiry', 0)

        # ⏱️ Expiré
        if time.time() > expiry:
            error_msg = "Mot de passe expiré, un nouveau a été envoyé"
            request.session.pop('admin_decrypt_hash', None)
            request.session.pop('admin_decrypt_expiry', None)

        # ✅ Correct
        elif password_hash == request.session.get('admin_decrypt_hash'):

            try:
                real_code = decrypt_code(code_obj.code)
            except:
                real_code = code_obj.code

            # 🧹 nettoyage
            request.session.pop('admin_decrypt_hash', None)
            request.session.pop('admin_decrypt_expiry', None)

        # ❌ Mauvais
        else:
            error_msg = "Mot de passe incorrect"

    # =========================================================
    # 3️⃣ Context
    # =========================================================
    context = {
        "code_obj": code_obj,
        "real_code": real_code,
        "error_msg": error_msg,
    }

    return render(request, "admin/code/reveal_code.html", context)

#================================== admin ===============================


@user_is_in_group('admin')  
def add_user(request):
    if request.method == 'POST':
        form = AddProfileForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Champs du formulaire
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

                    # 2️⃣ Attribution du groupe
                    group, created = Group.objects.get_or_create(name='reseller')
                    user.groups.add(group)

                    # 3️⃣ Création du Profile lié
                    profile = form.save(commit=False)
                    profile.user = user
                    profile.active = True
                    profile.save()

                    # 4️⃣ Envoi du mail HTML avec logo
                    logo_url = "https://ezrecnx.stripocdn.email/content/guids/CABINET_2ab71862352e04a3ba4522ed2a64ecde2ee6214a6a6abef3d49eb75423be291d/images/logob.png"

                    subject = "Your Account Has Been Created"
                    html_content = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; color: #333;">
                        <p>Hello {first_name},</p>

                        <p>Your account has been <strong>created</strong> by the admin on our platform.</p>

                        <hr style="border: none; border-top: 1px solid #ccc; margin: 20px 0;"/>

                        <p><strong>User Information:</strong></p>
                        <ul>
                            <li>Full Name: {first_name} {last_name}</li>
                            <li>Username: {username}</li>
                            <li>Email: {email}</li>
                            <li>Password: {password}</li>
                        </ul>

                        <p>You can now log in using your credentials.</p>

                        <br/>
                        <p>Best regards,<br/>
                        <strong>Your Platform Team</strong></p>

                        <img src="{logo_url}" alt="Platform Logo" style="height:50px; margin-top:20px;"/>
                    </body>
                    </html>
                    """

                    msg = EmailMultiAlternatives(
                        subject=subject,
                        body="",  # corps texte vide
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[email],
                    )
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()

                    messages.success(request, f"User {username} added successfully!")
                    return redirect('add_user')

            except Exception as e:
                messages.error(request, f"Erreur lors de l'ajout de l'utilisateur : {e}")
        else:
            messages.error(request, "Le formulaire est invalide. Vérifiez les champs.")
    else:
        form = AddProfileForm()

    context = {'form': form}
    return render(request, 'admin/user/add_user.html', context)


# liste user 
@user_is_in_group('admin')
def list_user(request):

    user = request.user

    # 🔹 PARTIE STATS
    achats = ProductAchat.objects.all()

    stats = achats.aggregate(
        pending=Count('id', filter=Q(status=StatusAchat.PENDING)),
        in_progress=Count('id', filter=Q(status=StatusAchat.IN_PROGRESS)),
        completed=Count('id', filter=Q(status=StatusAchat.COMPLETED)),
        rejected=Count('id', filter=Q(status=StatusAchat.REJECTED)),
        total=Count('id')
    )
    #-------------------  search -----------
    search = request.GET.get('search', '')

    #----------------- récupération du per_page --------
    per_page = request.GET.get('per_page', 10) 
    try:
        per_page = int(per_page)
    except:
        per_page = 10


    profile = Profile.objects.annotate(
    solde_total=Sum(
        'paiements__montant',
        filter=Q(paiements__active=True)
    )
).order_by('created_at')


    # -----------------------------------------
    if search:
        profile = profile.filter(
            Q(user__first_name__icontains=search) | Q(user__last_name__icontains=search) | Q(phone__icontains=search)| Q(user__email__icontains=search)| Q(user__username__icontains=search)
        )

    

    # ---------------Récupérer tous les paramètres GET sauf 'page' ------------
    params = request.GET.copy()
    if 'page' in params:
        params.pop('page')

    # ------------------Convertir en string utilisable dans les URLs-----------------
    querystring = params.urlencode() 

   
    paginator = Paginator(profile, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number) 
    
    

    context = {
       'page_obj': page_obj,
       'search': search,
       'querystring': querystring,
       'per_page': per_page,
       'stats': stats,
    }
    return render(request,'admin/user/list_user.html',context)



# activation du compte 
@user_is_in_group('admin')
@user_is_in_group('admin')
def toggle_profile_status(request, profil_id):
    profil = get_object_or_404(Profile, id=profil_id)

    # Inverser l'état
    profil.active = not profil.active
    profil.save()

    # Sujet du mail
    subject = "Your Account Has Been Activated" if profil.active else "Your Account Has Been Deactivated"

    # Lien direct vers le logo Stripo (CDN)
    logo_url = "https://ezrecnx.stripocdn.email/content/guids/CABINET_2ab71862352e04a3ba4522ed2a64ecde2ee6214a6a6abef3d49eb75423be291d/images/logob.png"

    # Contenu HTML
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <p>Hello {profil.user.username},</p>

        <p>Your account has been <strong>{'activated' if profil.active else 'deactivated'}</strong>
        {'by the administrator.' if profil.active else '.'}</p>

        {'<p>You can now log in to the platform.</p>' if profil.active else '<p>Please contact your administrator for more information.</p>'}

        <br/>
        <p>Best regards,<br/>
        <strong>The Platform Team</strong></p>

        <hr style="border: none; border-top: 1px solid #ccc; margin: 20px 0;"/>

        <!-- Logo via Stripo CDN -->
        <img src="{logo_url}" alt="Company Logo" style="height:50px;"/>
    </body>
    </html>
    """

    # Création et envoi du mail
    msg = EmailMultiAlternatives(
        subject=subject,
        body="",  # corps texte vide, on envoie HTML
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[profil.user.email]
    )
    msg.attach_alternative(body, "text/html")
    msg.send()

    # Message flash
    messages.success(
        request,
        f"The profile of {profil.user.username} has been "
        f"{'activated' if profil.active else 'deactivated'}."
    )

    return redirect('list_user')



# add category 
@user_is_in_group('admin')
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)  
        if form.is_valid():
            category = form.save(commit=False)
            category.active = True  
            category.save()
            return redirect('list_category')  
    else:
        form = CategoryForm()

    context = {
        'form': form
    }    
    
    return render(request, 'admin/category/add_category.html', context)

# list category
@user_is_in_group('admin','reseller')
def list_category(request):

    user = request.user

    # 🔹 PARTIE STATS
    achats = ProductAchat.objects.filter(profil__user=user)

    stats = achats.aggregate(
        pending=Count('id', filter=Q(status=StatusAchat.PENDING)),
        in_progress=Count('id', filter=Q(status=StatusAchat.IN_PROGRESS)),
        completed=Count('id', filter=Q(status=StatusAchat.COMPLETED)),
        rejected=Count('id', filter=Q(status=StatusAchat.REJECTED)),
        total=Count('id')
    )

    if request.user.groups.filter(name='admin').exists():
        # admin voit toutes les catégories
        category = Category.objects.filter(active=True).order_by('created_at')

    else:
        # reseller voit seulement ses catégories
        profil = request.user.profile
        category = profil.categories.filter(active=True).order_by('created_at')

    context = {
        'category': category,
        'stats': stats
    }

    return render(request, 'admin/category/list_category.html', context)





# list category
@user_is_in_group('admin')
def list_category_deactivate(request):
    category = Category.objects.filter(active=False).order_by('created_at')
    context = {
        'category':category
    }

    return render(request, 'admin/category/list_category_deactivate.html',context)


# edit category 
@user_is_in_group('admin')
def edit_category(request, cat_id):
    category = get_object_or_404(Category, id=cat_id)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            category = form.save(commit=False)
            if category.active == True :
             category.active = True
            else :
             category.active == False 

            category.save()
            messages.success(request, f"Produit '{category.name}' mis à jour avec succès !")
            return redirect('list_category')  # Redirige vers ta liste de produits
        else:
            messages.error(request, "Erreur lors de la mise à jour du produit.")
    else:
        form = CategoryForm(instance=category)
    
    context = {
        'form': form,
        'category': category,
    }
    return render(request, 'admin/category/edit_category.html', context)

@user_is_in_group('admin')
def deactivate_category(request,code):
        category = get_object_or_404(Category, id=code)

        # désactiver la catégorie
        category.active = False
        category.save()

        # désactiver toutes les sous-catégories de cette catégorie
        subcategories = category.subcategories.all()
        subcategories.update(active=False)

        # désactiver tous les produits qui appartiennent à ces sous-catégories
        Product.objects.filter(subcategory__in=subcategories).update(active=False)

        return redirect('list_category')

@user_is_in_group('admin')
def activate_category(request,code):
    category = get_object_or_404(Category, id=code)

    # désactiver la catégorie
    category.active = True
    category.save()

    # désactiver toutes les sous-catégories de cette catégorie
    subcategories = category.subcategories.all()
    subcategories.update(active=True)

    # désactiver tous les produits qui appartiennent à ces sous-catégories
    Product.objects.filter(subcategory__in=subcategories).update(active=True)
    return redirect ('list_category_deactivate')

# add subcategory 
@user_is_in_group('admin')
def add_subcategory(request):
    form = SubCategoryForm()

    if request.method == 'POST':
        
        form = SubCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            subcategory = form.save(commit=False)
            subcategory.active = True  # <-- forcer active à True
            subcategory.save()
            return redirect('list_subcategory')   
        else :
            form = SubCategoryForm()
    context = {
        'form': form
    }    

    return render(request, 'admin/subcategory/add_subcategory.html', context)

# list subcategory 
@user_is_in_group('admin')
def list_subcategory(request):
     #-------------------  search -----------
    search = request.GET.get('search', '')

    #----------------- récupération du per_page --------
    per_page = request.GET.get('per_page', 10) 
    try:
        per_page = int(per_page)
    except:
        per_page = 10

    subcategory = SubCategory.objects.all().filter(active=True).order_by('created_at')


        # -----------------------------------------
    if search:
        subcategory = subcategory.filter(
           Q(name__icontains=search)
        )

    

    # ---------------Récupérer tous les paramètres GET sauf 'page' ------------
    params = request.GET.copy()
    if 'page' in params:
        params.pop('page')

    # ------------------Convertir en string utilisable dans les URLs-----------------
    querystring = params.urlencode() 

   
    paginator = Paginator(subcategory, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number) 

    context = {
       'page_obj': page_obj,
       'search': search,
       'querystring': querystring,
       'per_page': per_page,
    }

    return render(request, 'admin/subcategory/list_subcategory.html',context)






# list subcategory 
@user_is_in_group('admin')
def list_subcategory_deactivate(request):
      #-------------------  search -----------
    search = request.GET.get('search', '')

    #----------------- récupération du per_page --------
    per_page = request.GET.get('per_page', 10) 
    try:
        per_page = int(per_page)
    except:
        per_page = 10

    subcategory = SubCategory.objects.all().filter(active=False).order_by('created_at')

         # -----------------------------------------
    if search:
        subcategory = subcategory.filter(
           Q(name__icontains=search)
        )

    

    # ---------------Récupérer tous les paramètres GET sauf 'page' ------------
    params = request.GET.copy()
    if 'page' in params:
        params.pop('page')

    # ------------------Convertir en string utilisable dans les URLs-----------------
    querystring = params.urlencode() 

   
    paginator = Paginator(subcategory, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number) 

    context = {
       'page_obj': page_obj,
       'search': search,
       'querystring': querystring,
       'per_page': per_page,
    }

    return render(request, 'admin/subcategory/list_subcategory_deactivate.html',context)




@user_is_in_group('admin')
def deactivate_subcategory(request,code):
    subcategory = get_object_or_404(SubCategory,id = code)
    subcategory.active = False
    subcategory.save()
    subcategory.plans.update(active=False)
    return redirect ('list_subcategory')

@user_is_in_group('admin')
def activate_subcategory(request,code):
    subcategory = get_object_or_404(SubCategory,id = code)
    subcategory.active = True
    subcategory.save()
    subcategory.plans.update(active=True)
    return redirect ('list_subcategory_deactivate')



@user_is_in_group('admin', 'reseller')
def product_list_by_id_deactivate(request, cat_id):
      #-------------------  search -----------
    search = request.GET.get('search', '')

    #----------------- récupération du per_page --------
    per_page = request.GET.get('per_page', 10) 
    try:
        per_page = int(per_page)
    except:
        per_page = 10

    subcategory = SubCategory.objects.filter(active=False).get(id=cat_id)
    product = subcategory.plans.filter(active=False)

    # -----------------------------------------
    if search:
        product = product.filter(
           Q(name__icontains=search)
        )

    
    # ---------------Récupérer tous les paramètres GET sauf 'page' ------------
    params = request.GET.copy()
    if 'page' in params:
        params.pop('page')

    # ------------------Convertir en string utilisable dans les URLs-----------------
    querystring = params.urlencode() 

   
    paginator = Paginator(product, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)     


    context = {
         'page_obj': page_obj,
        'search': search,
        'querystring': querystring,
        'per_page': per_page,
        'subcategory': subcategory
    }

    return render(request, 'admin/product/list_productid_deactivate.html', context)





# # edit subcategory 
@user_is_in_group('admin')
def edit_subcategory(request, subcat_id):
    subcategory = get_object_or_404(SubCategory, id=subcat_id)
    
    if request.method == 'POST':
        form = SubCategoryForm(request.POST, request.FILES, instance=subcategory)
        if form.is_valid():
            subcategory = form.save(commit=False)
            subcategory.active = True
            subcategory.save()
            messages.success(request, f"Produit '{subcategory.name}' mis à jour avec succès !")
            return redirect('list_subcategory')  # Redirige vers ta liste de produits
        else:
            messages.error(request, "Erreur lors de la mise à jour du produit.")
    else:
        form = SubCategoryForm(instance=subcategory)
    
    context = {
        'form': form,
        'subcategory': subcategory,
    }
    return render(request, 'admin/subcategory/edit_subcategory.html', context)


# add product 
@user_is_in_group('admin')
def add_product(request):
    form = ProductForm()

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            product = form.save(commit=False)
            product.active = True  # <-- forcer active à True
            product.save()
            return redirect('list_product')
        else : 
            form = ProductForm()

    context = {
         'form': form

    }        
    return render(request, 'admin/product/add_product.html', context)


# deactive product 
@user_is_in_group('admin')
def deactivate_product(request,code):
    product = get_object_or_404(Product,id = code)
    product.active = False
    product.save()
    return redirect ('list_product')
    
    
# active product 
@user_is_in_group('admin')
def activate_product(request,code):
    product = get_object_or_404(Product,id = code)
    product.active = True
    product.save()
    return redirect ('list_product_deactivate')
    
    

# list product 
@user_is_in_group('admin')
def list_product(request):
    #-------------------  search -----------
    search = request.GET.get('search', '')

    #----------------- récupération du per_page --------
    per_page = request.GET.get('per_page', 10) 
    try:
        per_page = int(per_page)
    except:
        per_page = 10

    
    product = Product.objects.all().filter(active=True).order_by('created_at')


    # -----------------------------------------
    if search:
        product = product.filter(
           Q(name__icontains=search)
        )

    

    # ---------------Récupérer tous les paramètres GET sauf 'page' ------------
    params = request.GET.copy()
    if 'page' in params:
        params.pop('page')

    # ------------------Convertir en string utilisable dans les URLs-----------------
    querystring = params.urlencode() 

   
    paginator = Paginator(product, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number) 
    
    

    context = {
       'page_obj': page_obj,
       'search': search,
       'querystring': querystring,
       'per_page': per_page,
    }
    return render(request,'admin/product/list_product.html',context)


# list product desactivte
@user_is_in_group('admin')
def list_product_deactivate(request):
    #-------------------  search -----------
    search = request.GET.get('search', '')

    #----------------- récupération du per_page --------
    per_page = request.GET.get('per_page', 10) 
    try:
        per_page = int(per_page)
    except:
        per_page = 10

    
    product = Product.objects.all().filter(active=False).order_by('created_at')


    # -----------------------------------------
    if search:
        product = product.filter(
           Q(name__icontains=search)
        )

    

    # ---------------Récupérer tous les paramètres GET sauf 'page' ------------
    params = request.GET.copy()
    if 'page' in params:
        params.pop('page')

    # ------------------Convertir en string utilisable dans les URLs-----------------
    querystring = params.urlencode() 

   
    paginator = Paginator(product, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number) 
    
    

    context = {
       'page_obj': page_obj,
       'search': search,
       'querystring': querystring,
       'per_page': per_page,
    }
    return render(request,'admin/product/list_product_deactivate.html',context)



# dupllicate product 
@user_is_in_group('admin')
def duplicate_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Dupliquer le produit
    new_product = Product.objects.create(
        subcategory=product.subcategory,
        name=f"{product.name} (Copie)",  # On peut ajouter "(Copie)" pour distinguer
        price=product.price,
        image=product.image,
        active=product.active
    )

    messages.success(request, f"Produit '{product.name}' dupliqué avec succès !")
    return redirect('list_product')

# edit product 

@user_is_in_group('admin')
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.active = True
            product.save()
            messages.success(request, f"Produit '{product.name}' mis à jour avec succès !")
            return redirect('list_product')  # Redirige vers ta liste de produits
        else:
            messages.error(request, "Erreur lors de la mise à jour du produit.")
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
    }
    return render(request, 'admin/product/edit_product.html', context)







# add activation code 
@user_is_in_group('admin')
def add_activation_code(request):
    form = ActivationCodeForm()

    if request.method == "POST":
        form = ActivationCodeForm(request.POST)

        if form.is_valid():
            product = form.cleaned_data['product']
            codes = request.POST.getlist('codes[]')
            errors = []

            for code in codes:
                code = code.strip()
                if code: 
                    code_hash = hashlib.sha256(code.encode()).hexdigest()

                    if ActivationCode.objects.filter(product=product, code=code).exists():
                        errors.append(f"Le code '{code}' existe déjà pour ce produit.")
                    else:
                        ActivationCode.objects.create(
                            product=product,
                            code=encrypt_code(code), 
                            code_hash=code_hash 
                        )

            # Recalcul du stock
            product.stock = product.activation_codes.filter(used=False).count()
            product.save()

            if errors:
                # Afficher les erreurs via messages framework
                for err in errors:
                    messages.error(request, err)
            else:
                messages.success(request, "Codes ajoutés avec succès !")
                return redirect('list_product')

    context = {
        'form': form
    }
    return render(request, 'admin/code/add_activation.html', context)

@user_is_in_group('admin')
def edit_activation_code(request, pk):
    activation_code = get_object_or_404(ActivationCode, pk=pk)
    form = EditActivationCodeForm(request.POST or None, instance=activation_code)

    if request.method == "POST" and form.is_valid():
        # commit=False pour pouvoir modifier le code et le hash avant de sauver
        activation_code = form.save(commit=False)

        # Récupérer le code entré par l'admin
        code = form.cleaned_data.get('code', '').strip()
        if code:
            # Encrypter le code
            activation_code.code = encrypt_code(code)

            # Calculer le hash
            activation_code.code_hash = hashlib.sha256(code.encode()).hexdigest()

        activation_code.save()

        messages.success(request, "Code modifié avec succès !")
        return redirect('list_activation_code', activation_code.product.id)

    context = {
        'form': form,
        'activation_code': activation_code,
    }
    return render(request, 'admin/code/edit_activation.html', context)
# @user_is_in_group('admin')
# def list_activation_by_product(request):

#     search = request.GET.get('search', '')

#     per_page = request.GET.get('per_page', 10)
#     try:
#         per_page = int(per_page)
#     except:
#         per_page = 10

#     # ➜ On récupère les produits AVEC leurs codes
#     products = Product.objects.prefetch_related('activation_codes')

#     # Recherche par code
#     if search:
#         products = products.filter(
#             activation_codes__code__icontains=search
#         ).distinct()

#     paginator = Paginator(products, per_page)
#     page_number = request.GET.get('page', 1)
#     page_obj = paginator.get_page(page_number)

#     context = {
#         'page_obj': page_obj,
#         'search': search,
#         'per_page': per_page,
#     }

#     return render(request, 'admin/code/list_activation_by_product.html', context)

@user_is_in_group('admin')
def generate_temp_password(request, profil_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    # Génération du mot de passe temporaire
    temp_password = secrets.token_urlsafe(8)
    temp_hash = hashlib.sha256(temp_password.encode()).hexdigest()
    request.session['montant_hash'] = temp_hash
    request.session['montant_expiry'] = time.time() + 60  # 60 secondes

    # Envoi de l'email
    send_mail(
        subject="Mot de passe temporaire pour ajouter montant",
        message=f"Votre mot de passe temporaire (valide 60s) : {temp_password}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[request.user.email],
        fail_silently=False,
    )

    return JsonResponse({"success": True})


# attirubution du montant pour chaque user 
@user_is_in_group('admin')
def add_montant(request):

    # 🔐 Vérification accès staff
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect(reverse('forbidden', kwargs={'code': 403}))

    profil_id = request.POST.get('profil_id')
    montant = request.POST.get('montant')
    password = request.POST.get('admin_password')

    if not profil_id or not montant or not password:
        return HttpResponseForbidden("Données invalides")

    # Vérification mot de passe temporaire
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if password_hash != request.session.get('montant_hash') or time.time() > request.session.get('montant_expiry', 0):
        messages.error(request, "Mot de passe temporaire invalide ou expiré")
        return redirect('list_user')

    profil = get_object_or_404(Profile, id=profil_id)
    Paiement.objects.create(
        profil=profil,
        montant=montant,
        
    )

    # Nettoyer la session
    request.session.pop('montant_hash', None)
    request.session.pop('montant_expiry', None)

    messages.success(request, "Montant ajouté avec succès")
    return redirect('list_user')

# list montant 
@user_is_in_group('admin')
def list_montant(request):

    search = request.GET.get('search', '')

    per_page = request.GET.get('per_page', 10)
    try:
        per_page = int(per_page)
    except:
        per_page = 10

    # ➜ On récupère les produits AVEC leurs codes
    profile = Profile.objects.prefetch_related('paiements')

    # Recherche par code
    if search:
        profile = profile.filter(
            paiements__codeP__icontains=search
        ).distinct()

    paginator = Paginator(profile, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search': search,
        'per_page': per_page,
    }

    return render(request, 'admin/amount/list_paiment.html', context)



# liste transaction user by id
@user_is_in_group('admin')
def list_transaction_by_code(request,id):
    profil = get_object_or_404(Profile, id=id)

    search = request.GET.get('search', '')

    per_page = request.GET.get('per_page', 10)
    try:
        per_page = int(per_page)
    except:
        per_page = 10

   
   
    montant = Paiement.objects.filter(profil=profil,montant__gt=0).order_by('-created_at')

    # Recherche par code
    if search:
        montant = montant.filter(
            profil__first_name__icontains=search
        ).distinct()

    paginator = Paginator(montant, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search': search,
        'per_page': per_page,
        'profil': profil,
    }

    return render(request, 'admin/amount/list_transaction.html', context)



# list subcateogry by id 
@user_is_in_group('admin', 'reseller')
def subcategory_list_by_id(request, cat_id):
      #-------------------  search -----------
    search = request.GET.get('search', '')

    #----------------- récupération du per_page --------
    per_page = request.GET.get('per_page', 10) 
    try:
        per_page = int(per_page)
    except:
        per_page = 10

    category = Category.objects.get(id=cat_id)
    subcategory = category.subcategories.filter(active = True)


      # -----------------------------------------
    if search:
        subcategory = subcategory.filter(
           Q(name__icontains=search)
        )

    

    # ---------------Récupérer tous les paramètres GET sauf 'page' ------------
    params = request.GET.copy()
    if 'page' in params:
        params.pop('page')

    # ------------------Convertir en string utilisable dans les URLs-----------------
    querystring = params.urlencode() 

   
    paginator = Paginator(subcategory, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number) 

    context = {
        'category': category,
         'page_obj': page_obj,
       'search': search,
       'querystring': querystring,
       'per_page': per_page,
    }

    return render(request, 'admin/subcategory/list_subcategory.html', context)


# list product by id 
@user_is_in_group('admin', 'reseller')
def product_list_by_id(request, cat_id):
      #-------------------  search -----------
    search = request.GET.get('search', '')

    #----------------- récupération du per_page --------
    per_page = request.GET.get('per_page', 10) 
    try:
        per_page = int(per_page)
    except:
        per_page = 10

    subcategory = SubCategory.objects.filter(active=True).get(id=cat_id)
    product = subcategory.plans.filter(active=True)

    # -----------------------------------------
    if search:
        product = product.filter(
           Q(name__icontains=search)
        )

    
    # ---------------Récupérer tous les paramètres GET sauf 'page' ------------
    params = request.GET.copy()
    if 'page' in params:
        params.pop('page')

    # ------------------Convertir en string utilisable dans les URLs-----------------
    querystring = params.urlencode() 

   
    paginator = Paginator(product, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)     


    context = {
         'page_obj': page_obj,
        'search': search,
        'querystring': querystring,
        'per_page': per_page,
        'subcategory': subcategory
    }

    return render(request, 'reseller/list_productid.html', context)




# list achat all user
@user_is_in_group('admin')
@user_is_in_group('admin')
def list_achat_user(request):
    search = request.GET.get('search', '')  
    per_page = request.GET.get('per_page', 10)

    try:
        per_page = int(per_page)
    except:
        per_page = 10

    # ✅ Tous les achats (pour admin)
    purchases = ProductAchat.objects.select_related('product', 'profil').prefetch_related('codes__activation_code')

    # Filtrer si recherche
    if search:
        search_hash = hashlib.sha256(search.encode()).hexdigest()  # hash du code saisi
        purchases = purchases.filter(
            Q(codeCP__icontains=search) |
            Q(profil__user__username__icontains=search) |
            Q(codes__activation_code__code_hash=search_hash)|
            Q(created_at__icontains=search)
        ).distinct()

    # Pagination
    paginator = Paginator(purchases.order_by('-created_at'), per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # 🔑 Déchiffrer tous les codes pour chaque achat
    for purchase in page_obj:
        purchase.decrypted_codes = []
        # Récupère tous les codes liés à cet achat
        codes = PurchaseCode.objects.filter(purchase=purchase).select_related('activation_code')
        for c in codes:
            try:
                real_code = decrypt_code(c.activation_code.code)
            except Exception:
                real_code = c.activation_code.code  # ancien code non chiffré
            purchase.decrypted_codes.append(real_code)

    context = {
        'page_obj': page_obj,
        'search': search,
        'per_page': per_page,
    }

    return render(request, 'admin/purchase/list_achat_user.html', context)



# affiche details achat 
@user_is_in_group('admin')
def admin_detail_achats(request, codeCP):
    # 🔐 Vérification admin (optionnel)
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('forbidden')  # ou ta page d'erreur

    # Récupère l'achat correspondant au codeCP
    purchase = get_object_or_404(ProductAchat, codeCP=codeCP)

    # Codes liés à cet achat
    codes = purchase.codes.all()

    # 🔑 Déchiffrer les codes
    decrypted_codes = []
    for c in codes:
        try:
            real_code = decrypt_code(c.activation_code.code)
        except:
            real_code = c.activation_code.code  # pour anciens codes non chiffrés
        decrypted_codes.append(real_code)

    # récupérer remboursement
    refund = Paiement.objects.filter(
        profil=purchase.profil,
        type=Paiement.TypePaiement.REFUND,
        montant=purchase.total_price
    ).order_by('-created_at').first()

    context = {
        'purchase': purchase,
        'codes': codes,
        'decrypted_codes': decrypted_codes,  # 🔑 ajouté pour le template
        'refund': refund
    }

    return render(request, 'admin/purchase/detail_achat_user.html', context)

@user_is_in_group('admin')
def edit_request(request, pk):
    request_achat = get_object_or_404(ProductAchat, pk=pk)

    old_status = request_achat.status  # Sauvegarde l'ancien statut

    if request.method == "POST":
        form = ProductRequestUpdateForm(request.POST, instance=request_achat)
        if form.is_valid():
            updated_purchase = form.save(commit=False)  # Ne sauvegarde pas encore
            new_status = updated_purchase.status

            # Si le statut passe à rejected et qu'il était différent avant
            if new_status == StatusAchat.REJECTED and old_status != StatusAchat.REJECTED:
                profil = request_achat.profil

                # Remboursement
                Paiement.objects.create(
                    profil=profil,
                    montant=request_achat.total_price,  
                    type=Paiement.TypePaiement.REFUND,
                    active=True
                )

                creer_notification_refund(updated_purchase)

            updated_purchase.save()  # Enregistre les modifications
            

            # Redirection vers la liste des achats après mise à jour
            return redirect('list_achat_user')
    else:
        form = ProductRequestUpdateForm(instance=request_achat)

    context = {
        'form': form,
        'request_achat': request_achat
    }

    return render(request, 'admin/purchase/edit_achat_request.html', context)





def admin_check(user):
    return user.is_superuser or user.groups.filter(name='admin').exists()

@user_passes_test(admin_check)
def assign_categories(request, profil_id):
    profil = get_object_or_404(Profile, id=profil_id)
    categories = Category.objects.filter(active=True)

    if request.method == 'POST':
        form = UserCategoryForm(request.POST, instance=profil)
        if form.is_valid():
            form.save()
            return redirect('list_user')  # redirige vers la liste des users
    else:
        form = UserCategoryForm(instance=profil)

    context = {
        'form': form, 
        'profil': profil,
        'categories': categories
       
   }     

    return render(request, 'admin/category/assign_categories.html', context)

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

@user_is_in_group('admin')
def log_code(request):
    #-------------------  search -----------
    search = request.GET.get('search', '')

    #----------------- récupération du per_page --------
    per_page = request.GET.get('per_page', 10) 
    try:
        per_page = int(per_page)
    except:
        per_page = 10

    
    log_code = ActivationCodeLog.objects.all().order_by('timestamp')


    # -----------------------------------------
    if search:
        log_code = log_code.filter(
           Q(action__icontains=search)
        )

    

    # ---------------Récupérer tous les paramètres GET sauf 'page' ------------
    params = request.GET.copy()
    if 'page' in params:
        params.pop('page')

    # ------------------Convertir en string utilisable dans les URLs-----------------
    querystring = params.urlencode() 

   
    paginator = Paginator(log_code, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number) 
    
    

    context = {
       'page_obj': page_obj,
       'search': search,
       'querystring': querystring,
       'per_page': per_page,
    }
    return render(request,'admin/code/list_log.html',context)



# liste code 
# Vérification admin
def admin_check(user):
    return user.is_active and user.groups.filter(name='admin').exists()

@user_passes_test(admin_check)
def list_activation_code(request, id):
    # Récupère le produit
    product = get_object_or_404(Product, id=id)

    # Double vérification côté vue
    if not request.user.groups.filter(name='admin').exists():
        return HttpResponseForbidden("You are not allowed to view this page.")
    
    ip = get_client_ip(request)
    browser = get_browser(request)

    # Enregistrement du log dans la base
    ActivationCodeLog.objects.create(
        user=request.user,
        product_id=product.id,
        action="Accessed activation codes",
        ip_address=ip,
        browser=browser
    )

    # Gestion recherche
    search = request.GET.get('search', '')

    # Gestion pagination
    per_page = request.GET.get('per_page', 10)
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 10

    # Récupère tous les codes liés au produit
    codes = ActivationCode.objects.filter(product=product).order_by('-created_at')

    # Filtre par recherche si nécessaire
    if search:
        
        search_hash = hashlib.sha256(search.encode()).hexdigest()

        codes = codes.filter(
            Q(code_hash=search_hash)
        ).distinct()

    # Pagination
    paginator = Paginator(codes, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Context pour le template
    context = {
        'page_obj': page_obj,
        'search': search,
        'per_page': per_page,
        'product': product,
    }

    return render(request, 'admin/code/list_code_activation.html', context)










# ================================ reseller ==========================

# buy code 
@user_is_in_group('reseller')
def buy_product(request):
    if request.method != "POST":
        return JsonResponse({'success': False}, status=400)

    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity'))
    note = request.POST.get('note', '')
    requirement = request.POST.get('requirement', '')
    

    product = get_object_or_404(Product, id=product_id)
    profil = request.user.profile

    total_price = product.price * quantity

    solde = profil.paiements.filter(active=True).aggregate(
        total=Sum('montant')
    )['total'] or Decimal('0')

    if solde < total_price:
        return JsonResponse({
            'success': False,
            'error': f"Insufficient balance : {solde} DA."
        })

    category_type = product.subcategory.category.type_category
    product_type = product.type_product

    if category_type == CatgoryType.CODE and product_type == ProductType.CODE and quantity > product.stock:
        return JsonResponse({
            'success': False,
            'error': "Insufficient stock."
        })

    reste = solde - total_price

    with transaction.atomic():

        if category_type == CatgoryType.CODE and product_type == ProductType.CODE:

            status = StatusAchat.COMPLETED

            codes = list(
                ActivationCode.objects
                .select_for_update()
                .filter(product=product, used=False)[:quantity]
            )

            if len(codes) < quantity:
                return JsonResponse({
                    'success': False,
                    'error': "Not enough codes available."
                })

        elif category_type == CatgoryType.CODE and product_type == ProductType.REQUEST:
            status = StatusAchat.PENDING
            codes = []

        elif category_type == CatgoryType.REQUEST:
            status = StatusAchat.PENDING
            codes = []

      


        purchase = ProductAchat.objects.create(
            profil=profil,
            product=product,
            quantity=quantity,
            total_price=total_price,
            note=note,
            reste_after_purchase=reste,
            status=status,
            requirement=requirement if product_type == ProductType.REQUEST or category_type == CatgoryType.REQUEST else None,
               
        )

        purchased_codes = []

        if status == StatusAchat.COMPLETED:
            for code in codes:
                code.used = True
                code.used_at = timezone.now()
                code.save()

                PurchaseCode.objects.create(
                    purchase=purchase,
                    activation_code=code
                )

                # purchased_codes.append(code.code)
                # 🔓 DÉCHIFFREMENT ICI
                real_code = decrypt_code(code.code)
                purchased_codes.append(real_code)

            product.stock -= quantity
            product.save()

        Paiement.objects.create(
            profil=profil,
            montant=-total_price,
            active=True
        )

         # 📩 Envoi email si REQUEST
        if status == StatusAchat.PENDING:
            messages.success(request, "Your request has been submitted successfully and is pending approval.")
            send_mail(
                    subject="New Request Submitted",
                    message=f"""
                Hello Admin,

                A new request has been submitted. Please find the details below:

                -----------------------------
                User Information:
                Name     : {profil.user.first_name} {profil.user.last_name}
                Username : {profil.user.username}
                Email    : {profil.user.email}

                Product Information:
                Product  : {product.name}
                Quantity : {quantity}
                Total Price : {total_price} 

                Additional Details:
                Note : {note}
                Requirement: {requirement}
                -----------------------------

                Please take the necessary action.

                Best regards,
                Your System
                    """,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ADMIN_NOTIFICATION_EMAIL],
                    fail_silently=False,
            )
            
            creer_notification_request(purchase)    

    return JsonResponse({
        'success': True,
        'codes': purchased_codes,
        'total_price': str(total_price)
    })


# list activation user
@user_is_in_group('reseller')
def list_activation_user(request):
    search = request.GET.get('search', '')  # Recherche par code
    per_page = request.GET.get('per_page', 10)

    try:
        per_page = int(per_page)
    except:
        per_page = 10

    # Tous les codes achetés par le revendeur connecté
    codes = PurchaseCode.objects.filter(
        purchase__profil=request.user.profile
    ).select_related('activation_code', 'purchase', 'purchase__product')

    # Filtrer si recherche
    if search:
        codes = codes.filter(activation_code__code__icontains=search)

    # Pagination
    paginator = Paginator(codes.order_by('-created_at'), per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)


    for code in page_obj:
        try:
            code.decrypted_code = decrypt_code(code.activation_code.code)
        except:
            code.decrypted_code = code.activation_code.code 

    context = {
        'page_obj': page_obj,
        'search': search,
        'per_page': per_page,
    }

    return render(request, 'reseller/list_activation_user.html', context)


# transaction 
@user_is_in_group('reseller')
def history_transaction(request):
    search = request.GET.get('search', '')  # Recherche par code
    per_page = request.GET.get('per_page', 10)

    try:
        per_page = int(per_page)
    except:
        per_page = 10

    # Récupérer tous les codes achetés par le revendeur connecté
    profil = request.user.profile

    paiements = Paiement.objects.filter(profil=profil, montant__gt=0).order_by('-created_at')

    # Filtrer si une recherche est saisie
    if search:
        paiements = paiements.filter(
            profil__user__first_name__icontains=search
        )

    # Pagination
    paginator = Paginator(paiements.order_by('-created_at'), per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search': search,
        'per_page': per_page,
    }

    return render(request, 'reseller/history_transaction.html', context)



# list achat all user 
@user_is_in_group('reseller')  
def list_achat(request):
    search = request.GET.get('search', '')  
    per_page = request.GET.get('per_page', 10)

    try:
        per_page = int(per_page)
    except:
        per_page = 10

    # ✅ seulement les achats du user connecté
    products = ProductAchat.objects.filter(profil__user=request.user)

    # Recherche
    if search:
        search_hash = hashlib.sha256(search.encode()).hexdigest()
        products = products.filter(
            Q(product__name__icontains=search) |
            Q(codeCP__icontains=search) |
            Q(product__activation_codes__code_hash=search_hash)
        ).distinct()

    # Pagination
    paginator = Paginator(products.order_by('-created_at'), per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Déchiffrer tous les codes pour chaque achat
    for purchase in page_obj:
        purchase.decrypted_codes = []
        # Récupère tous les codes liés à ce produit et à cet achat
        codes = PurchaseCode.objects.filter(purchase=purchase).select_related('activation_code')
        for c in codes:
            try:
                real_code = decrypt_code(c.activation_code.code)
            except:
                real_code = c.activation_code.code  # ancien code non chiffré
            purchase.decrypted_codes.append(real_code)

    context = {
        'page_obj': page_obj,
        'search': search,
        'per_page': per_page,
    }

    return render(request, 'reseller/list_achat.html', context)




@user_is_in_group('reseller')
def detail_achat(request, codeCP):
    profil = request.user.profile
    purchase = get_object_or_404(ProductAchat, codeCP=codeCP, profil=profil)
    codes = purchase.codes.all()

      # Déchiffrer les codes
    decrypted_codes = []
    for c in codes:
        try:
            real_code = decrypt_code(c.activation_code.code)
        except:
            real_code = c.activation_code.code  # pour anciens codes non chiffrés
        decrypted_codes.append(real_code)

     # récupérer remboursement
    refund = Paiement.objects.filter(
        profil=profil,
        type=Paiement.TypePaiement.REFUND,
        montant=purchase.total_price
    ).order_by('-created_at').first()

    context = {
        'purchase': purchase,
        'decrypted_codes': decrypted_codes,
        'reste': purchase.reste_after_purchase ,
        'refund': refund
    }

    return render(request, 'reseller/detail_achat.html', context)





@require_POST
@login_required
def mark_notifications_as_read(request):
    if request.user.groups.filter(name='Admin').exists():
        Notification.objects.filter(is_read=False).update(is_read=True)
    else:
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'ok'})


