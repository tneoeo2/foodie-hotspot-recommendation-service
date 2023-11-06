from rest_framework import serializers
from .models import Restaurant

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = (
            'id',
            'longitude', 
            'latitude', 
            'score'
        )
    
    def validate_score(self, value):
        if value < 0 or value > 5:
            raise serializers.ValidationError("평점(score)은 0에서 5 사이어야 합니다.")
        return value