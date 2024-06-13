from rest_framework import serializers
from djangoapp.models.test import Test


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = '__all__'
