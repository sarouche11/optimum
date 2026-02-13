from django.shortcuts import render
from authentification.decorators import user_is_in_group
from authentification.models import Profile
from .models import Category,SubCategory,Product,ActivationCode,Paiement,ProductAchat,PurchaseCode
from .forms import CategoryForm, SubCategoryForm, ProductForm, ActivationCodeForm,PaiementForm
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from decimal import Decimal
from django.db.models import Sum,Prefetch
from django.utils import timezone





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


    profile = Profile.objects.all().order_by('created_at')


    # -----------------------------------------
    if search:
        profile = profile.filter(
            Q(user__first_name__icontains=search) | Q(user__last_name__icontains=search) | Q(phone__icontains=search)| Q(user__email__icontains=search)
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
        profil.user.email_user(
            "Activation de votre compte",
            f"Bonjour {profil.user.username},\n\n"
            "Votre compte a été activé par l’administrateur.\n"
            "Vous pouvez maintenant vous connecter à la plateforme.\n\n"
            "Cordialement."
        )
    else : 
         profil.user.email_user(
            "Désactivation de votre compte",
            f"Bonjour {profil.user.username},\n\n"
            "Votre compte a été désactivé.\n"
            "Veuillez contactez votre administrateur pour plus d'information.\n\n"
            "Cordialement."
        )


    messages.success(
        request,
        f"Le profil de {profil.user.username} a été "
        f"{'activé' if profil.active else 'désactivé'}."
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
    
    return render(request, 'admin/add_category.html', context)

# list category
@user_is_in_group('admin','reseller')
def list_category(request):
    category = Category.objects.all().filter(active=True).order_by('created_at')
    context = {
        'category':category
    }

    return render(request, 'admin/list_category.html',context)


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

    return render(request, 'admin/add_subcategory.html', context)

# list subcategory 
@user_is_in_group('admin')
def list_subcategory(request):
    subcategory = SubCategory.objects.all().filter(active=True).order_by('created_at')
    context = {
        'subcategory':subcategory
    }

    return render(request, 'admin/list_subcategory.html',context)

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
    return render(request, 'admin/add_product.html', context)


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
    return render(request,'admin/list_product.html',context)


# add activation code 
@user_is_in_group('admin')
def add_activation_code(request):
    form = ActivationCodeForm()

    if request.method == "POST":
        form = ActivationCodeForm(request.POST)
        if form.is_valid():
            activation_code = form.save(commit=False)  # on ne sauvegarde pas encore
            activation_code.save()  # on sauvegarde le code
            form.save()

             # Recalcul du stock à partir de tous les codes non utilisés
            product = activation_code.product
            product.stock = product.activation_codes.filter(used=False).count()
            product.save()
            return redirect('list_activation')   # à adapter selon ta route

    context = {
        'form': form
    }
    return render(request, 'admin/add_activation.html', context)


# add activation code 

@user_is_in_group('admin')
def edit_activation_code(request, pk):
    # On récupère le code existant
    activation_code = get_object_or_404(ActivationCode, pk=pk)

    # Formulaire pré-rempli avec les données existantes
    form = ActivationCodeForm(request.POST or None, instance=activation_code)

    if request.method == "POST" and form.is_valid():
        # Sauvegarde les modifications
        activation_code = form.save()


        return redirect('list_activation')  # adapte selon ta route

    context = {
        'form': form,
        
    }
    return render(request, 'admin/edit_activation.html', context)




# liste code by product 
@user_is_in_group('admin')
def list_activation_by_product(request):

    search = request.GET.get('search', '')

    per_page = request.GET.get('per_page', 10)
    try:
        per_page = int(per_page)
    except:
        per_page = 10

    # ➜ On récupère les produits AVEC leurs codes
    products = Product.objects.prefetch_related('activation_codes')

    # Recherche par code
    if search:
        products = products.filter(
            activation_codes__code__icontains=search
        ).distinct()

    paginator = Paginator(products, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search': search,
        'per_page': per_page,
    }

    return render(request, 'admin/list_activation_by_product.html', context)


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
   
    code = ActivationCode.objects.filter(product=product)

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

    return render(request, 'admin/list_code_activation.html', context)



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




# liste code 
@user_is_in_group('admin')
def list_transaction_by_code(request,id):
    profil = get_object_or_404(Profile, id=id)

    search = request.GET.get('search', '')

    per_page = request.GET.get('per_page', 10)
    try:
        per_page = int(per_page)
    except:
        per_page = 10

    # ➜ On récupère les code pour chaque produit
   
    montant = Paiement.objects.filter(profil=profil)

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

    return render(request, 'admin/list_transaction.html', context)



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

    return render(request, 'admin/list_paiment.html', context)


# list subcateogry by id 
@user_is_in_group('admin', 'reseller')
def subcategory_list_by_id(request, cat_id):
    category = Category.objects.get(id=cat_id)
    subcategory = category.subcategories.all()

    context = {
        'category': category,
        'subcategory': subcategory
    }

    return render(request, 'admin/list_subcategory.html', context)


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

    subcategory = SubCategory.objects.get(id=cat_id)
    product = subcategory.plans.all()

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

    # produit +quantité 
    product = ProductAchat.objects.all()
    # Filtrer si recherche
    if search:
        product = product.filter(product__name__icontains=search)

    # Pagination
    paginator = Paginator(product.order_by('-created_at'), per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search': search,
        'per_page': per_page,
    }

    return render(request, 'admin/list_achat_user.html', context)




# ================================ reseller ==========================

# buy code 
@user_is_in_group('reseller')
def buy_product(request):
    if request.method != "POST":
        return redirect('list_activation_user')

    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity'))
    note = request.POST.get('note', '')

    product = get_object_or_404(Product, id=product_id)
    profil = request.user.profile
    total_price = product.price * quantity

    # ===== CALCUL SOLDE =====
    solde = profil.paiements.filter(active=True).aggregate(total=Sum('montant'))['total'] or Decimal('0')

    # ===== 1. VERIF STOCK =====
    if quantity > product.stock:
        messages.error(request, "Stock insuffisant pour ce produit.")
        return redirect('list_activation_user')

    # ===== 2. VERIF SOLDE =====
    if solde < total_price:
        messages.error(request, f"Solde insuffisant : votre solde est de {solde} DA alors que l'achat coûte {total_price} DA.")
        return redirect('list_activation_user')

    # ===== 3. VERIF CODES DISPONIBLES =====
    codes = list(ActivationCode.objects.filter(product=product, used=False)[:quantity])
    if len(codes) < quantity:
        messages.error(request, "Pas assez de codes d'activation disponibles.")
        return redirect('list_activation_user')

    # ===== 4. CREER L'ACHAT =====
    purchase = ProductAchat.objects.create(
        profil=profil,
        product=product,
        quantity=quantity,
        total_price=total_price,
        note=note
    )

    # ===== 5. Lier les codes à l'achat =====
    for code in codes:
        code.used = True
        code.used_at = timezone.now()
        code.save()

        PurchaseCode.objects.create(
            purchase=purchase,
            activation_code=code
        )

    # ===== 6. REDUIRE LE STOCK =====
    product.stock -= quantity
    product.save()

    # ===== 7. CREER LE PAIEMENT =====
    Paiement.objects.create(
        profil=profil,
        montant=-total_price,
        active=True
    )

    messages.success(request, f"Achat réussi : {quantity} code(s) pour {total_price} DA.")
    return redirect('list_activation_user')

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
@user_is_in_group('reseller')  # ⚠️ attention ici, je t’explique dessous
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
        product = product.filter(product__name__icontains=search)

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



