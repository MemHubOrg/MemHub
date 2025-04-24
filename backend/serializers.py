from rest_framework import serializers
from .models import Template, Meme

# Сериализатор для GET (возвращает imageUrl)
class TemplateSerializer(serializers.ModelSerializer):
    imageUrl = serializers.SerializerMethodField()

    class Meta:
        model = Template
        fields = ['id', 'imageUrl', 'created_at']

    def get_imageUrl(self, obj):
        return obj.image.url if obj.image else None

# Сериализатор для POST (загрузка файла)
class TemplateUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = ['image']


class MemeSerializer(serializers.ModelSerializer):
    imageUrl = serializers.SerializerMethodField()
    userId = serializers.ReadOnlyField(source='user.id')

    class Meta:
        model = Meme
        fields = ['id', 'imageUrl', 'created_at', 'userId']

    def get_imageUrl(self, obj):
        return obj.image.url if obj.image else None


class MemeUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meme
        fields = ['image']