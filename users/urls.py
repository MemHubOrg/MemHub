from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('profile/', views.profile, name='profile'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('my_memes/', views.my_memes_view, name='my_memes'),
    path('selected_meme/<int:image_id>/', views.selected_meme_view, name='selected_meme'),
]
