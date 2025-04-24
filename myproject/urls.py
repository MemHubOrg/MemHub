"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from register.views import CustomTokenView

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


schema_view = get_schema_view(
   openapi.Info(
      title="MemHub API",
      default_version='v1.0.11',
      description="Документация для API MemHub",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', include('users.urls')),  # подключаем urls приложения users
#     path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Обновление токена
#     path('api/token/', CustomTokenView.as_view(), name='token_obtain_pair'),
# ]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('register.urls')),  # подключаем urls приложения register
    path('api/', include('backend.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    #path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Получение токена
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Обновление токена
    path('api/token/', CustomTokenView.as_view(), name='token_obtain_pair'),
    path('captcha/', include('captcha.urls')),
    path('users/', include(('users.urls', 'users'), namespace='users'))
]

# Для доступа к изображениям
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
