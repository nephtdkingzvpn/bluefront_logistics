from django.urls import path

from . import views

app_name = 'account'

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('create_shipment/', views.create_new_shipment, name='create_shipment'),
    path('delete_shipment/<pk>/', views.delete_shipment, name='delete_shipment'),
]
