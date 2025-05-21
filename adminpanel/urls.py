from django.urls import path
from . import views

urlpatterns = [
    path('', views.adminpanel_index, name='adminpanel_index'),
    path('login/', views.admin_login, name='admin_login'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('templates/', views.manage_templates, name='manage_templates'),
    path('toggle-ban/', views.toggle_ban, name='toggle_ban'),
    path('kick-sessions/', views.kick_sessions, name='kick_sessions'),
    path('request-password-reset/', views.request_password_reset_flag),
]
