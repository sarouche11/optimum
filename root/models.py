from django.db import models
import random
from django.contrib.auth.models import User
from authentification.models import Profile
from django.db.models import Sum
from decimal import Decimal
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

def generate_code():
    return ''.join(random.choices('AZERTYUIOPQSDFGHJKLMWXCVBN123456789', k=10))


class CatgoryType(models.TextChoices):
    
    REQUEST   = 'request', _('Request')
    CODE      = 'code', _('Code')    
       
    


# 1. Catégorie principale (IPTV, VOD, etc.)
class Category(models.Model):
    code_cat = models.CharField(max_length=100, unique=True, default=generate_code)
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='categories/')
    type_category = models.CharField(choices=CatgoryType.choices, max_length=20,)
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



class ProductType(models.TextChoices):
    
    REQUEST   = 'request', _('Request')
    CODE      = 'code', _('Code') 

# 3. Produit / Plan d’abonnement
class Product(models.Model):
    code_product = models.CharField(max_length=100, unique=True, default=generate_code)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="plans")
    name = models.CharField(max_length=150)       
    price = models.IntegerField()
    stock = models.PositiveIntegerField(default=0) 
    image = models.ImageField(upload_to='products/')
    type_product = models.CharField(choices=ProductType.choices, max_length=20,)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class ActivationCode(models.Model):
    code_activ = models.CharField(max_length=100, unique=True, default=generate_code)
    code = models.TextField() 
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="activation_codes")
    used = models.BooleanField(default=False)  
    code_hash = models.CharField(max_length=64, db_index=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('product', 'code_hash')

    def __str__(self):
        return f"{self.product.name}- {self.code_activ} "
    
# Signal pour diminuer le stock à la suppression d'un code
@receiver(pre_delete, sender=ActivationCode)
def decrease_product_stock(sender, instance, **kwargs):
    product = instance.product
    if product.stock > 0:
        product.stock -= 1
        product.save()  



class Paiement(models.Model):

    class TypePaiement(models.TextChoices):
        DEBITE = "debite", "Debited"
        CREDITE = "credite", "Credited"
        REFUND = "refund", "Remboursement"

    codeP = models.CharField(max_length=100, unique=True, default=generate_code)
    profil = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='paiements')
    montant = models.IntegerField()
    type = models.CharField(max_length=20, choices=TypePaiement.choices, default=TypePaiement.CREDITE)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.profil.user.username}"
    



class StatusAchat(models.TextChoices):
    
    PENDING   = 'pending', _('Pending')
    IN_PROGRESS      = 'in_progress', _('In_progress')    
    COMPLETED      = 'completed', _('Completed')    
    REJECTED      = 'rejected', _('Rejected')    
    



class ProductAchat(models.Model):
    codeCP = models.CharField(max_length=100, unique=True, default=generate_code)
    profil = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="code_purchases")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="purchases",null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.IntegerField()
    note = models.TextField(null=True, blank=True)
    reste_after_purchase = models.IntegerField()
    requirement = models.CharField(max_length=255, null=True, blank=True)
    answer = models.CharField(max_length=255, null=True, blank=True)
    reason = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=StatusAchat.choices, default=StatusAchat.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)


   
    def __str__(self):
        return f"{self.profil.user.username} → {self.product.name} ({self.quantity})"


class PurchaseCode(models.Model):
    codePur = models.CharField(max_length=100, unique=True, default=generate_code)
    purchase = models.ForeignKey(ProductAchat, on_delete=models.CASCADE, related_name="codes")
    activation_code = models.OneToOneField(ActivationCode, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.activation_code.code
    



class Notification(models.Model):
    codeN = models.CharField(default=generate_code, editable=False, unique=True,max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.message[:20]}"
    


class ActivationCodeLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255, default="Accessed activation codes")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    browser = models.TextField(null=True, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Product {self.product} - {self.timestamp}"    

