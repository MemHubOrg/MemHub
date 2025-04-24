from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TemplateViewSet, MemeViewSet, UserMeView

router = DefaultRouter()
router.register(r'templates', TemplateViewSet, basename='template')
router.register(r'memes', MemeViewSet, basename='meme')

urlpatterns = [
    path('', include(router.urls)),
    path('user/me/', UserMeView.as_view(), name='user-me'),
]