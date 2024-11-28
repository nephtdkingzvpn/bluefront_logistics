from django.urls import path

from . import views

app_name = 'frontend'

urlpatterns = [
    path('', views.home, name="home"),
    path('track-shipment/', views.track_shipment, name="track_shipment"),
    path('login/', views.loginUser, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('about_us/', views.about_us, name='about_us'),
    path('service/', views.service, name='service'),
    path('contact_us/', views.contact_us, name='contact_us'),
]