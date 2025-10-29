from django.urls import path
from . import views

urlpatterns = [
    # ... inne ścieżki
    path('admin/inventory/raport-komputerow/', computers_report, name='admin_computers_report'),
]
