from rest_framework import serializers
from .models import Item, UserKey

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

class AuthorizedKeySerializer(serializers.Serializer):
    email = serializers.EmailField()
    key = serializers.CharField()

class UserKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserKey
        fields = ["email", "key", "created_at"]
