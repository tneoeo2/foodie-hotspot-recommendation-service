from django.conf import settings
from rest_framework import serializers
from foodiehotspots.models import Restaurant

logger = settings.CUSTOM_LOGGER

class RestaurantInfoUpdateSerializers(serializers.ModelSerializer):
    class Meta():
        model = Restaurant
   
        exclude = ['name_address','score']
 
    
    def set_name_address(self, validated_data):
        name = validated_data.get('name')
        address_lotno = validated_data.get('address_lotno')
        address_roadnm = validated_data.get('address_roadnm')

        if name:
            if address_lotno:
                validated_data['name_address'] = f"{name} {address_lotno}"
            elif address_roadnm:
                validated_data['name_address'] = f"{name} {address_roadnm}"
    
                    
    def create(self, validated_data):
        logger.debug('create test----------')
        self.set_name_address(validated_data)
        restaurant = Restaurant(**validated_data)
        restaurant.save()
        # restaurant, created = Restaurant.objects.get_or_create(name_address=validated_data['name_address'], defaults=validated_data)
        # logger.info(f'created : {created}')   #false면 기존에 있던데이터
        
        return restaurant
    
    def update(self, instance, validated_data):
        # 변경된 필드 확인
        IS_CHANGED = False
        changed_fields = {}
        for attr, value in validated_data.items():
            try:
                if getattr(instance, attr) != value:
                    changed_fields[attr] = value
            except Exception as e:
                    logger.error(f'update ERROR : {e}')
                    
        self.set_name_address(validated_data)  #주소 바뀔 시 반영
                    
        for attr, value in changed_fields.items():
            setattr(instance, attr, value)
            
        if len(changed_fields) != 0:
            IS_CHANGED == True
            instance.save()  
            logger.debug(f'변경된 필드 : {changed_fields}, 개수 : {len(changed_fields)} ')
            
        return IS_CHANGED
