from django.urls import path
from .views import (list_user ,toggle_profile_status,
                    add_category,list_category,edit_category,
                    add_subcategory,list_subcategory,edit_subcategory,
                    add_product,list_product,
                    add_activation_code,edit_activation_code,list_activation_code,
                    add_montant,list_montant,list_transaction_by_code,
                    list_activation_by_product,
                    subcategory_list_by_id,product_list_by_id,
                    list_achat_user,admin_detail_achats,
                    duplicate_product,edit_product,

                    buy_product,list_activation_user,
                     history_transaction,
                   list_achat,
                    detail_achat,edit_request)

urlpatterns = [

    # admin
    path('list_user/', list_user, name='list_user'),
    path('toggle-profile/<int:profil_id>/',toggle_profile_status, name='toggle_profile_status'),

    path('add_category/', add_category, name='add_category'),
    path('list_category/', list_category, name='list_category'),
    path('edit-category/<int:cat_id>/', edit_category, name='edit_category'),

    path('add_subcategory/', add_subcategory, name='add_subcategory'),
    path('list_subcategory/', list_subcategory, name='list_subcategory'),
    path('edit-subcategory/<int:subcat_id>/', edit_subcategory, name='edit_subcategory'),

    path('add_product/', add_product, name='add_product'),
    path('list_product/', list_product, name='list_product'),


    
    path('list_activation_code/<int:id>', list_activation_code, name='list_activation_code'),
    path('add_activation/', add_activation_code, name='add_activation'),
    path('edit_activation_code/<int:pk>', edit_activation_code, name='edit_activation_code'),

    path('list_activation/', list_activation_by_product, name='list_activation'),


    path('add_montant/', add_montant, name='add_montant'),
    path('list_montant/', list_montant, name='list_montant'),

    # liste transaction user by id ( coté admin )
    path('list_transaction/<int:id>', list_transaction_by_code, name='list_transaction'),

    path('subcategory/<int:cat_id>/', subcategory_list_by_id, name='subcategory_list'),
    path('product/<int:cat_id>/', product_list_by_id, name='product_list'),

    path('list_achat_user/', list_achat_user, name='list_achat_user'),
    path('detail_achat_user/<str:codeCP>/', admin_detail_achats, name='detail_achat_user'),

    path('duplicate-product/<int:product_id>/', duplicate_product, name='duplicate_product'),
    
    path('edit-product/<int:product_id>/', edit_product, name='edit_product'),

    path('purchase/edit/<int:pk>/', edit_request, name='edit_request'),
    
   




#    reseller 
    path('buy-product/', buy_product, name='buy_product'),
    path('list_activation_user/', list_activation_user, name='list_activation_user'),
    
    path('list_achat/', list_achat, name='list_achat'),
    path('detail_achat/<str:codeCP>/', detail_achat, name='detail_achat'),

    path('history_transaction/', history_transaction, name='history_transaction'),

    
    ]