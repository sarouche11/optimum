from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Category,SubCategory,Product,ActivationCode, Paiement , ProductAchat,PurchaseCode

@admin.register(Category)
class CategoryImportExport(ImportExportModelAdmin):
    fields = [
        'name',
        'type_category',
        'image',
        'active',
    ]

    list_display = [
        'code_cat',
        'name',
        'type_category',
        'image',
        'active',
        'created_at',
        'updated_at',
       
    ]

    search_fields = ['name']
    list_filter = ['active']

@admin.register(SubCategory)
class SubCategoryImportExport(ImportExportModelAdmin):
    fields = [
        'category',
        'name',
        'image',
        'active',
    ]

    list_display = [
        'code_subcat',
        'category',
        'name',
        'image',
        'active',
        'created_at',
        'updated_at',
       
    ]

    search_fields = ['name']
    list_filter = ['active']

@admin.register(Product)
class ProductImportExport(ImportExportModelAdmin):
    fields = [
        'subcategory',
        'name',
        'price',
        'stock',
        'image',
        'active',
    ]

    list_display = [
        'code_product',
        'subcategory',
        'name',
        'price',
        'stock',
        'image',
        'active',
        'created_at',
        'updated_at',
       
    ]

    search_fields = ['name']
    list_filter = ['active']

@admin.register(ActivationCode)
class ActivationCodeImportExport(ImportExportModelAdmin):
    fields = [
       'code',
        'product',
        'used',
    ]

    list_display = [
        'code_activ',
        'code',
        'product',
        'used',
        'created_at',
        'used_at',
        
       
    ]

    search_fields = ['code']
    list_filter = ['used']

@admin.register(Paiement)
class PaiementImportExport(ImportExportModelAdmin):
    fields = [
        'profil',
        'montant',
        'active',
       
    ]

    list_display = [
        'codeP',
        'profil',
        'montant',
        'active',
        'created_at',
        'updated_at',
        
       
    ]

    search_fields = ['codeP']
    list_filter = ['active']


@admin.register(ProductAchat)
class ProductAchatImportExport(ImportExportModelAdmin):
    fields = [
        'profil',
        'product',
        'quantity',
        'total_price',
        'note',
        'status',
        'active',
       
    ]

    list_display = [
        'codeCP',
        'profil',
        'product',
        'quantity',
        'total_price',
        'note',
        'status',
        'active',
        'created_at',
        'updated_at',
        
       
    ]

    search_fields = ['codeCP']
    list_filter = ['active']


@admin.register(PurchaseCode)
class PurchaseCodeImportExport(ImportExportModelAdmin):
    fields = [
        'purchase',
        'activation_code',
        'active',
       
    ]

    list_display = [
        'codePur',
        'purchase',
        'activation_code',
        'active',
        'created_at',
        'updated_at',
        
       
    ]

    search_fields = ['codeCP']
    list_filter = ['active']
