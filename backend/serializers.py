# from rest_framework import serializers
# from .models import Template, Meme, Tag
#
# class TagSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Tag
#         fields = ['name']
#
# # Сериализатор для GET (возвращает imageUrl)
# class TemplateSerializer(serializers.ModelSerializer):
#     imageUrl = serializers.SerializerMethodField()
#     tags = TagSerializer(many=True)
#     class Meta:
#         model = Template
#         fields = ['id', 'imageUrl', 'created_at', 'tags']
#
#     def get_imageUrl(self, obj):
#         return obj.image_url
#
# # Сериализатор для POST (загрузка файла)
# class TemplateUploadSerializer(serializers.ModelSerializer):
#     tags = serializers.ListField(
#         child=serializers.CharField(max_length=32),
#         allow_empty=True,
#         max_length=3,
#         required=False
#     )
#     class Meta:
#         model = Template
#         fields = ['image_url', 'tags']
#
#     def create(self, validated_data):
#         tag_names = validated_data.pop('tags', [])
#         template = Template.objects.create(**validated_data)
#         for name in tag_names[:3]:  # ограничение на 3 тега
#             tag, _ = Tag.objects.get_or_create(name=name.lower())
#             template.tags.add(tag)
#         return template
#
# class MemeSerializer(serializers.ModelSerializer):
#     imageUrl = serializers.SerializerMethodField()
#     userId = serializers.ReadOnlyField(source='user.id')
#
#     class Meta:
#         model = Meme
#         fields = ['id', 'imageUrl', 'created_at', 'userId']
#
#     def get_imageUrl(self, obj):
#         return obj.image_url
#
#
# class MemeUploadSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Meme
#         fields = ['image_url']
from rest_framework import serializers
from .models import Template, Meme#, Tag

# Сериализатор для GET (возвращает imageUrl)
# class TagSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Tag
#         fields = ['name']
class TemplateSerializer(serializers.ModelSerializer):
    imageUrl = serializers.SerializerMethodField()  # поле для отображения URL изображения
    # tags = TagSerializer(many=True)
    tags = serializers.SerializerMethodField()
    class Meta:
        model = Template
        fields = ['id', 'imageUrl', 'created_at', 'tags']  # добавляем поле imageUrl для отображения

    def get_imageUrl(self, obj):
        return obj.image_url  # возвращаем URL из поля image_url

    def get_tags(self, obj):
        return obj.tags  # просто возвращаем содержимое JSONField
# class TemplateSerializer(serializers.ModelSerializer):
#     imageUrl = serializers.SerializerMethodField()
#     tags = TagSerializer(many=True)
#     class Meta:
#         model = Template
#         fields = ['id', 'imageUrl', 'created_at', 'tags']
#
#     def get_imageUrl(self, obj):
#         return obj.image_url


# Сериализатор для POST (загрузка файла)
class TemplateUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = ['image_url']  # работаем только с image_url


class MemeSerializer(serializers.ModelSerializer):
    imageUrl = serializers.SerializerMethodField()  # поле для отображения URL
    userId = serializers.ReadOnlyField(source='user.id')

    class Meta:
        model = Meme
        fields = ['id', 'imageUrl', 'created_at', 'userId']

    def get_imageUrl(self, obj):
        return obj.image_url  # возвращаем image_url, так как это строка с URL


class MemeUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meme
        fields = ['image_url']  # работаем только с image_url