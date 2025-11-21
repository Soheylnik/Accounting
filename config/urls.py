from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('accounts/', include('apps.accounts.urls')),
#     path('chart/', include('apps.chartofaccounts.urls')),
#     path('journal/', include('apps.journals.urls')),
#     path('ledger/', include('apps.ledger.urls')),
#     path('costcenters/', include('apps.costcenters.urls')),
#     path('tags/', include('apps.tagsystem.urls')),
#     path('invoices/', include('apps.invoices.urls')),
#     path('payments/', include('apps.payments.urls')),
#     path('banking/', include('apps.banking.urls')),
#     path('reports/', include('apps.financialreports.urls')),
]
