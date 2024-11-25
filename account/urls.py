from django.urls import path

from . import views

app_name = 'account'

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('create_shipment/', views.create_new_shipment, name='create_shipment'),
    path('edit_shipment/<pk>/', views.edit_shipment, name='edit_shipment'),
    path('shipment_details/<pk>/', views.shipment_detail, name='shipment_detail'),
    path('delete_shipment/<pk>/', views.delete_shipment, name='delete_shipment'),
]
