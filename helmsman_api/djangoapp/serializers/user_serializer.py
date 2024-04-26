from rest_framework import serializers
from djangoapp.models.user import User
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        password = validated_data.pop('password', None)

        if password:
            validated_data['password'] = make_password(password)

        return super().create(validated_data)