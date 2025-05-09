from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Template, Meme
from .serializers import TemplateSerializer, MemeSerializer, TemplateUploadSerializer, MemeUploadSerializer
from django.contrib.auth.models import User
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models.expressions import RawSQL


class TemplateViewSet(viewsets.ModelViewSet):
    queryset = Template.objects.all()
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action == 'create':
            return TemplateUploadSerializer
        return TemplateSerializer

    def get_queryset(self):
        queryset = Template.objects.all()
        tag_query = self.request.query_params.get('tag')

        if tag_query:
            # Подстрочный поиск по JSON-массиву tags
            queryset = queryset.annotate(
                tag_match=RawSQL(
                    "EXISTS (SELECT 1 FROM jsonb_array_elements_text(tags) AS tag WHERE tag ILIKE %s)",
                    [f"%{tag_query}%"]
                )
            ).filter(tag_match=True)

        return queryset
# class TemplateViewSet(viewsets.ModelViewSet):
#     queryset = Template.objects.all()
#     permission_classes = [permissions.AllowAny]
#
#     def get_serializer_class(self):
#         if self.action == 'create':
#             return TemplateUploadSerializer
#         return TemplateSerializer
#
#     parser_classes = [MultiPartParser, FormParser]

class MemeViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action == 'create':
            return MemeUploadSerializer
        return MemeSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Meme.objects.filter(user=user)
        return Meme.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": str(user.id),
            "username": user.username,
            "login": user.username  # подставляется Telegram login
        })