from django.urls import path
from .views import (list_user ,toggle_profile_status,add_category,
                    list_category,add_subcategory,list_subcategory,add_product,list_product,
                    list_activation_by_product,add_activation_code,add_montant,list_montant,
                    subcategory_list_by_id,product_list_by_id,
                    buy_product,list_activation_user,list_activation_code,
                    list_transaction_by_code, edit_activation_code,history_transaction,
                    list_achat_user,list_achat,
                    detail_achat,admin_detail_achats)

urlpatterns = [

    # admin
    path('list_user/', list_user, name='list_user'),
    path('toggle-profile/<int:profil_id>/',toggle_profile_status, name='toggle_profile_status'),

    path('add_category/', add_category, name='add_category'),
    path('list_category/', list_category, name='list_category'),

    path('add_subcategory/', add_subcategory, name='add_subcategory'),
    path('list_subcategory/', list_subcategory, name='list_subcategory'),

    path('add_product/', add_product, name='add_product'),
    path('list_product/', list_product, name='list_product'),


    path('list_activation/', list_activation_by_product, name='list_activation'),
    path('add_activation/', add_activation_code, name='add_activation'),
    path('edit_activation_code/<int:pk>', edit_activation_code, name='edit_activation_code'),

    path('add_montant/', add_montant, name='add_montant'),
    path('list_montant/', list_montant, name='list_montant'),

    path('list_activation_code/<int:id>', list_activation_code, name='list_activation_code'),
    path('list_transaction/<int:id>', list_transaction_by_code, name='list_transaction'),

    path('subcategory/<int:cat_id>/', subcategory_list_by_id, name='subcategory_list'),
    path('product/<int:cat_id>/', product_list_by_id, name='product_list'),

    path('list_achat_user/', list_achat_user, name='list_achat_user'),
    
    path('detail_achat_user/<str:codeCP>/', admin_detail_achats, name='detail_achat_user'),
    
    path('detail_achat/<str:codeCP>/', detail_achat, name='detail_achat'),

   




#    reseller 
    path('buy-product/', buy_product, name='buy_product'),
    path('list_activation_user/', list_activation_user, name='list_activation_user'),
    path('list_achat/', list_achat, name='list_achat'),
    path('history_transaction/', history_transaction, name='history_transaction'),

    
    ]