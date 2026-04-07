from django.urls import path
from .views import (reveal_activation_code,list_user ,add_user,toggle_profile_status,toggle_totp,
                    add_category,list_category,edit_category,deactivate_category,activate_category,
                    list_category_deactivate,
                    
                    add_subcategory,list_subcategory,edit_subcategory,deactivate_subcategory,activate_subcategory,
                    list_subcategory_deactivate,

                    add_product,list_product,list_product_deactivate,activate_product,
                    duplicate_product,edit_product,deactivate_product,product_list_by_id_deactivate,

                    add_activation_code,edit_activation_code,list_activation_code,log_code,

                    add_montant,list_montant,list_transaction_by_code,generate_temp_password,
                    
                    subcategory_list_by_id,product_list_by_id,

                    list_achat_user,admin_detail_achats,
                    assign_categories,

                    buy_product, list_activation_user,

                    history_transaction,
                     
                   list_achat,

                    detail_achat,edit_request,
                  
                    mark_notifications_as_read)

urlpatterns = [

    # admin
    path("admin/reveal-code/<int:code_id>/", reveal_activation_code, name="reveal_activation_code"),


    path('list_user/', list_user, name='list_user'),
    path('add_user/', add_user, name='add_user'),
    path('toggle-profile/<int:profil_id>/',toggle_profile_status, name='toggle_profile_status'),

    path('toggle-totp/<int:profil_id>/',toggle_totp, name='toggle_totp'),

    path('add_category/', add_category, name='add_category'),
    path('list_category/', list_category, name='list_category'),
    path('list_category_deactivate/', list_category_deactivate, name='list_category_deactivate'),
    path('edit-category/<int:cat_id>/', edit_category, name='edit_category'),
    path('deactivate_category/<int:code>', deactivate_category, name='deactivate_category'),
    path('activate_category/<int:code>', activate_category, name='activate_category'),

    path('add_subcategory/', add_subcategory, name='add_subcategory'),
    path('list_subcategory/', list_subcategory, name='list_subcategory'),
    path('list_subcategory_deactivate/', list_subcategory_deactivate, name='list_subcategory_deactivate'),
    path('edit-subcategory/<int:subcat_id>/', edit_subcategory, name='edit_subcategory'),
    path('deactivate_subcategory/<int:code>', deactivate_subcategory, name='deactivate_subcategory'),
    path('activate_subcategory/<int:code>', activate_subcategory, name='activate_subcategory'),


    path('add_product/', add_product, name='add_product'),
    path('list_product/', list_product, name='list_product'),
    path('list_product_deactivate/', list_product_deactivate, name='list_product_deactivate'),
    path('deactivate_product/<int:code>', deactivate_product, name='deactivate_product'),
    path('activate_product/<int:code>', activate_product, name='activate_product'),

    path('product_deactivate/<int:cat_id>/', product_list_by_id_deactivate, name='product_list_by_id_deactivate'),


    
    path('list_activation_code/<int:id>', list_activation_code, name='list_activation_code'),
    path('add_activation/', add_activation_code, name='add_activation'),
    path('edit_activation_code/<int:pk>', edit_activation_code, name='edit_activation_code'),
    path('log_code', log_code, name='log_code'),

    # path('list_activation/', list_activation_by_product, name='list_activation'),

    path('generate-temp-password/<int:profil_id>/', generate_temp_password, name='generate_temp_password'),
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

    path('categories/assigned/<int:profil_id>/', assign_categories, name='assign_categories'),


    
   




#    reseller 
    path('buy-product/', buy_product, name='buy_product'),
    path('list_activation_user/', list_activation_user, name='list_activation_user'),
    
    path('list_achat/', list_achat, name='list_achat'),
    path('detail_achat/<str:codeCP>/', detail_achat, name='detail_achat'),

    path('history_transaction/', history_transaction, name='history_transaction'),
    






    # notification 

    path('notifications/read/', mark_notifications_as_read, name='notifications_lues'),



    
    ]