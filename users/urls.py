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
    path('delete_meme/<int:meme_id>/', views.delete_meme, name='delete_meme'),
    path("shared/<uuid:token>/", views.shared_meme_view, name="shared_meme"),
    path("api/create-share-link/", views.create_temp_link, name="create_share_link"),
]

handler404 = 'django.views.defaults.page_not_found'
handler400 = 'django.views.defaults.bad_request'
handler403 = 'django.views.defaults.permission_denied'
handler500 = 'django.views.defaults.server_error'