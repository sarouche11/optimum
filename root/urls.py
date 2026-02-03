from django.urls import path
from .views import (list_user, list ,toggle_profile_status,add_category,
                    list_category,add_subcategory,list_subcategory,add_product,list_product,
                    list_activation,add_activation_code,add_montant,list_montant)

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


    path('list_activation/', list_activation, name='list_activation'),
    path('add_activation/', add_activation_code, name='add_activation'),

    path('add_montant/', add_montant, name='add_montant'),
    path('list_montant/', list_montant, name='list_montant'),




#    reseller 
    path('list/', list, name='list'),
    
    ]