from rest_framework import serializers
from django.contrib.auth import get_user_model

class UserDetailUpdateSerializers(serializers.ModelSerializers):
    class Meta():
        model = get_user_model()
        fields = ['latitude', 'longitude', 'recommand_active']
        read_only_fields = ['user_name']
        
        