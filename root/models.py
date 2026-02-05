from django.db import models
import random
from authentification.models import Profile

def generate_code():
    return ''.join(random.choices('AZERTYUIOPQSDFGHJKLMWXCVBN123456789', k=10))


# 1. Catégorie principale (IPTV, VOD, etc.)
class Category(models.Model):
    code_cat = models.CharField(max_length=100, unique=True, default=generate_code)
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='categories/')
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# 2. Sous-catégorie (Jupiter, Iron, Atlas...)
class SubCategory(models.Model):
    code_subcat = models.CharField(max_length=100, unique=True, default=generate_code)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='sub_categories/')
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"


# 3. Produit / Plan d’abonnement
class Product(models.Model):
    code_product = models.CharField(max_length=100, unique=True, default=generate_code)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="plans")
    name = models.CharField(max_length=150)       
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0) 
    image = models.ImageField(upload_to='products/')
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class ActivationCode(models.Model):
    code_activ = models.CharField(max_length=100, unique=True, default=generate_code)
    code = models.CharField(max_length=50, unique=True) 
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="activation_codes")
    used = models.BooleanField(default=False)  
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.code} "



class Paiement(models.Model):
    codeP = models.CharField(max_length=100, unique=True, default=generate_code)
    profil = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='paiements')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.profil.user.username}"
    

class CodePurchase(models.Model):
    codeCP = models.CharField(max_length=100, unique=True, default=generate_code)
    profil = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="code_purchases")
    activation_code = models.OneToOneField(ActivationCode, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.profil.user.username} → {self.activation_code.code}"    