from django.urls import path
from .views import login_view,verify_otp,forbidden,logout_view,register_view,success


urlpatterns = [

    path('', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('verify_otp/', verify_otp, name='verify_otp'),
    path('register/', register_view, name='register'),
    path('success/', success, name='success'),
    path('forbidden/<int:code>/', forbidden, name='forbidden'),

    
    ]