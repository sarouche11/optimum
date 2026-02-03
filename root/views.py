from django.shortcuts import render
from authentification.decorators import user_is_in_group
from authentification.models import Profile
from .models import Category,SubCategory,Product,ActivationCode,Paiement
from .forms import CategoryForm, SubCategoryForm, ProductForm, ActivationCodeForm,PaiementForm
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse



# Create your views here.

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


@user_is_in_group('admin')
def toggle_profile_status(request, profil_id):
    profil = get_object_or_404(Profile, id=profil_id)

    # Inverser l'état
    profil.active = not profil.active
    profil.save()

    messages.success(
        request,
        f"Le profil de {profil.user.username} a été {'activé' if profil.active else 'désactivé'}."
    )

    return redirect('list_user')



@user_is_in_group('admin')
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)  
        if form.is_valid():
            form.save()
            return redirect('list_category')  
    else:
        form = CategoryForm()

    context = {
        'form': form
    }    
    
    return render(request, 'admin/add_category.html', context)

def list_category(request):
    category = Category.objects.all().order_by('created_at')
    context = {
        'category':category
    }

    return render(request, 'admin/list_category.html',context)




def add_subcategory(request):
    form = SubCategoryForm()

    if request.method == 'POST':
        
        form = SubCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('list_subcategory')   
        else :
            form = SubCategoryForm()
    context = {
        'form': form
    }    

    return render(request, 'admin/add_subcategory.html', context)



def list_subcategory(request):
    subcategory = SubCategory.objects.all().order_by('created_at')
    context = {
        'subcategory':subcategory
    }

    return render(request, 'admin/list_subcategory.html',context)



def add_product(request):
    form = ProductForm()

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('list_product')
        else : 
            form = ProductForm()

    context = {
         'form': form

    }        
    return render(request, 'admin/add_product.html', context)



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


    product = Product.objects.all().order_by('created_at')


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




def add_activation_code(request):
    form = ActivationCodeForm()

    if request.method == "POST":
        form = ActivationCodeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_activation')   # à adapter selon ta route

    context = {
        'form': form
    }
    return render(request, 'admin/add_activation.html', context)



@user_is_in_group('admin')
def list_activation(request):

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

    return render(request, 'admin/list_activation.html', context)




@user_is_in_group('admin')
def attribuer_montant(request, profile_id):
    profil = get_object_or_404(Profile, id=profile_id)

    if request.method == "POST":
        form = PaiementForm(request.POST)
        if form.is_valid():
            paiement = form.save(commit=False)
            paiement.profil = profil
            paiement.save()
            return redirect('list_user')
    else:
        form = PaiementForm()

    context = {
        'form': form, 
        'profil': profil

    }    

    return render(request, 'admin/list_user.html', context)



@user_is_in_group('admin')
def add_montant(request):
    
    print("POST =", request.POST) 
    profil_id = request.POST.get('profil_id')
    montant = request.POST.get('montant')

    if not profil_id or not montant:
        return HttpResponse("Données manquantes", status=400)

    profil = get_object_or_404(Profile, id=profil_id)

    Paiement.objects.create(
        profil=profil,
        montant=montant,
    )

    return redirect('list_user')




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


@user_is_in_group('reseller')
def list(request):
    return render(request,'reseller/list.html')

