from rest_framework import serializers
from djangoapp.models.group import Group

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'
