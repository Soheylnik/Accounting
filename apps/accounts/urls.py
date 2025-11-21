from django.urls import path
from .views import *
app_name = 'accounts'
urlpatterns = [
    path('register/', registerView.as_view(), name='register'),
    path('login/', loginView.as_view(), name='login'),
]