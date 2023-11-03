from rest_framework import serializers
from django.contrib.auth import get_user_model


from accounts.models import Location

class UserDetailUpdateSerializers(serializers.ModelSerializer):
    class Meta():
        model = get_user_model()
        fields = ['latitude', 'longitude', 'recommand_active']
        read_only_fields = ['user_name']
        

class LocationSerializers(serializers.ModelSerializer):
    class Meta():
        model = Location
        fields = ['dosi', 'sgg', 'longitude', 'latitude']