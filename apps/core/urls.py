from django.urls import path
from .views import *
app_name = 'core'
urlpatterns = [
    path('', indexView.as_view(), name='index'),
    path('dashboard/', DashboardHomeView.as_view(), name='dashboard_home'),
]
