from django.shortcuts import render
from authentification.decorators import user_is_in_group
from authentification.models import Profile
from .models import (Category,SubCategory,Product,ActivationCode,Paiement,
                     ProductAchat,PurchaseCode,CatgoryType,StatusAchat,ProductType,Notification)
from .forms import (CategoryForm, SubCategoryForm, 
                    ProductForm, ActivationCodeForm,EditActivationCodeForm,ProductRequestUpdateForm)
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from decimal import Decimal
from django.db.models import Sum,Prefetch
from django.utils import timezone
from django.http import JsonResponse
from django.db import transaction

from django.core.mail import send_mail
from django.conf import settings


from .utils import creer_notification_request,creer_notification_refund
from django.views.decorators.http import require_POST
from .context_processors import get_notifications
from django.contrib.auth.decorators import login_required




#================================== admin ===============================

# liste user 
@user_is_in_group('admin')
def list_user(request):
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
    }
    return render(request,'admin/list_user.html',context)

# activation du compte 
@user_is_in_group('admin')
def toggle_profile_status(request, profil_id):
    profil = get_object_or_404(Profile, id=profil_id)

    # Inverser l'état
    profil.active = not profil.active
    profil.save()

        # ✅ Si le compte vient d’être activé → envoyer email
    if profil.active:
        subject = "Your Account Has Been Activated"
        body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <p>Hello {profil.user.username},</p>

        <p>Your account has been <strong>activated</strong> by the administrator.</p>
        <p>You can now log in to the platform.</p>

        <br/>
        <p>Best regards,<br/>
        <strong>The Platform Team</strong></p>

        <hr style="border: none; border-top: 1px solid #ccc; margin: 20px 0;"/>

        <!-- Logo -->
        <img src="https://panel.digiddel.com/staticfiles/assets/images" alt="Company Logo" style="height:50px;">

        <!-- Contact info -->
        <p style="font-size: 12px; color: #555;">
        Email: contact@yourcompany.com | Phone: +123 456 7890 | Website: <a href="https://panel.digideel.com">Digideel</a>
        </p>
    </body>
    </html>
    """
    else:
        subject = "Your Account Has Been Deactivated"
        body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <p>Hello {profil.user.username},</p>

        <p>Your account has been <strong>deactivated</strong>.</p>
        <p>Please contact your administrator for more information.</p>

        <br/>
        <p>Best regards,<br/>
        <strong>The Platform Team</strong></p>

        <hr style="border: none; border-top: 1px solid #ccc; margin: 20px 0;"/>

        <!-- Logo -->
        <img src="https://panel.digiddel.com/panel/staticfiles/assets/images" alt="Company Logo" style="height:50px;">

        <!-- Contact info -->
        <p style="font-size: 12px; color: #555;">
        Email: contact@yourcompany.com | Phone: +123 456 7890 | Website: <a href="https://panel.digideel.com">Digideel</a>
        </p>
    </body>
    </html>
    """

    profil.user.email_user(
        subject=subject,
        message="",  
        html_message=body
    )
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
            category.active = True  # <-- forcer active à True
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
    category = Category.objects.filter(active=True).order_by('created_at')
    context = {
        'category':category
    }

    return render(request, 'admin/category/list_category.html',context)

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
    subcategory = SubCategory.objects.all().filter(active=True).order_by('created_at')
    context = {
        'subcategory':subcategory
    }

    return render(request, 'admin/subcategory/list_subcategory.html',context)






# list subcategory 
@user_is_in_group('admin')
def list_subcategory_deactivate(request):
    subcategory = SubCategory.objects.all().filter(active=False).order_by('created_at')
    context = {
        'subcategory':subcategory
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
                if code:  # éviter les champs vides
                    # Vérifier si le code existe déjà pour ce produit
                    if ActivationCode.objects.filter(product=product, code=code).exists():
                        errors.append(f"Le code '{code}' existe déjà pour ce produit.")
                    else:
                        ActivationCode.objects.create(
                            product=product,
                            code=code
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
    # On récupère le code existant
    activation_code = get_object_or_404(ActivationCode, pk=pk)

    # Formulaire pré-rempli avec les données existantes
    form = EditActivationCodeForm(request.POST or None, instance=activation_code)

    if request.method == "POST" and form.is_valid():
        # Sauvegarde les modifications
        activation_code = form.save()
        messages.success(request,'code modifié avec succés')


        return redirect('list_activation_code',  activation_code.product.id)  # adapte selon ta route

    context = {
        'form': form,
        
    }
    return render(request, 'admin/code/edit_activation.html', context)



# liste code 
@user_is_in_group('admin')
def list_activation_code(request,id):
    product = get_object_or_404(Product, id=id)

    search = request.GET.get('search', '')

    per_page = request.GET.get('per_page', 10)
    try:
        per_page = int(per_page)
    except:
        per_page = 10

    # ➜ On récupère les code pour chaque produit
   
    code = ActivationCode.objects.filter(product=product).order_by('-created_at')

    # Recherche par code
    if search:
        code = code.filter(
            code__icontains=search
        ).distinct()

    paginator = Paginator(code, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search': search,
        'per_page': per_page,
        'product': product,
    }

    return render(request, 'admin/code/list_code_activation.html', context)



# liste code by product 
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




# attirubution du montant pour chaque user 
@user_is_in_group('admin')
def add_montant(request):
    
    print("POST =", request.POST) 
    profil_id = request.POST.get('profil_id')
    montant = request.POST.get('montant')

    if not profil_id or not montant:
        return HttpResponse("Données manquantes", status=400)
    
    messages.success(request, "Montant attribué avec succés.")

    profil = get_object_or_404(Profile, id=profil_id)

    Paiement.objects.create(
        profil=profil,
        montant=montant,
    )

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
    category = Category.objects.get(id=cat_id)
    subcategory = category.subcategories.filter(active = True)

    context = {
        'category': category,
        'subcategory': subcategory
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
def list_achat_user(request):
    search = request.GET.get('search', '')  
    per_page = request.GET.get('per_page', 10)

    try:
        per_page = int(per_page)
    except:
        per_page = 10

    purchases = ProductAchat.objects.select_related('product', 'profil').prefetch_related('codes__activation_code')

    # Filtrer si recherche
    if search:
        purchases = purchases.filter(
            Q(product__name__icontains=search) |
            Q(codeCP__icontains=search) |
            Q(profil__user__username__icontains=search) |
            Q(created_at__icontains=search)|
            Q (product__activation_codes__code__icontains=search)
        )


       

    # Pagination
    paginator = Paginator(purchases.order_by('-created_at'), per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search': search,
        'per_page': per_page,
       

    }

    return render(request, 'admin/purchase/list_achat_user.html', context)



# affiche details achat 
@user_is_in_group('admin')
def admin_detail_achats(request, codeCP):
    # Récupère l'achat correspondant au codeCP
    purchase = get_object_or_404(ProductAchat, codeCP=codeCP)
    
    # Codes liés à cet achat
    codes = purchase.codes.all()

     # récupérer remboursement
    refund = Paiement.objects.filter(
        profil=purchase.profil,
        type=Paiement.TypePaiement.REFUND,
        montant=purchase.total_price
    ).order_by('-created_at').first()

    context = {
        'purchase': purchase,
        'codes': codes,
        'refund':refund
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

                purchased_codes.append(code.code)

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
                Total Price : {total_price} DA

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
    product = ProductAchat.objects.filter(profil__user=request.user)

    # Recherche
    if search:
        product = product.filter(
          Q(product__name__icontains=search) | Q (codeCP__icontains=search)| Q (product__activation_codes__code__icontains=search)
          )

    # Pagination
    paginator = Paginator(product.order_by('-created_at'), per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

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

     # récupérer remboursement
    refund = Paiement.objects.filter(
        profil=profil,
        type=Paiement.TypePaiement.REFUND,
        montant=purchase.total_price
    ).order_by('-created_at').first()

    context = {
        'purchase': purchase,
        'codes': codes,
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
