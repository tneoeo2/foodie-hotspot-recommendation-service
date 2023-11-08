from rest_framework import serializers
from django.contrib.auth import get_user_model

class UserDetailUpdateSerializers(serializers.ModelSerializer):
    class Meta():
        model = get_user_model()
        fields = ['latitude', 'longitude', 'is_recommend']
        read_only_fields = ['user_name']
        
        