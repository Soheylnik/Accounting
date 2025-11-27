from django.urls import path
from .views import *
app_name = 'accounts'
urlpatterns = [
    path('register/', registerView.as_view(), name='register'),
    path('login/', loginView.as_view(), name='login'),
    path('logout/', logoutView.as_view(), name='logout'),
    path('verify-phone/', VerifyPhoneView.as_view(), name='verify_phone'),
]