from django.urls import path
from .views import login_view,verify_otp,forbidden,logout_view,register_view,success,edit_profile,change_password


urlpatterns = [

    path('', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('verify_otp/', verify_otp, name='verify_otp'),
    path('register/', register_view, name='register'),
    path('success/', success, name='success'),
    path('profile/', edit_profile, name='profile'),
    path('profile/change-password/', change_password, name='change_password'),
    
    path('forbidden/<int:code>/', forbidden, name='forbidden'),

    
    ]