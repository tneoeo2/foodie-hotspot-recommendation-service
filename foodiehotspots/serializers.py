from django.conf import settings
from rest_framework import serializers
from foodiehotspots.models import Restaurant
from .models import Restaurant, Rate
from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField, SerializerMethodField


logger = settings.CUSTOM_LOGGER


class EvalCreateSerializers(ModelSerializer):
    model = Rate
    field = ['score', 'content']
    
class FoodieDetailsSerializers(ModelSerializer):

    related_eval_ids = SerializerMethodField()
    
    
    def get_related_eval_ids(self, obj):
        # 해당 company_id로 지원한 지원공고인 recruit_id를 리스트로 반환
        related_evals = Rate.objects.filter(restaurant=obj.id).order_by('-created_at')
        #value_list를 사용하면 object에서 지정해준 field값을 tuple형태로 return 해줍니다.
        evals_ids = related_evals.values_list('score','content')
        return evals_ids
    
    class Meta:
        model = Restaurant
        fields = '__all__'
        
class RestaurantInfoUpdateSerializers(serializers.ModelSerializer):
    class Meta():
        model = Restaurant
        fields = ['sgg', 'sgg_code', 'name', 'start_date', 'business_state', 'closed_date'
                  ,'local_area', 'water_facility', 'male_employee_cnt', 'year', 'multi_used', 'multi_used'
                  ,'grade_sep', 'total_area', 'female_employee_cnt', 'buisiness_site', 'sanitarity'
                  ,'food_category', 'employee_cnt', 'address_lotno', 'address_roadnm', 'zip_code'
                  ,'longitude', 'latitude']
        # fields = '__all__'
    
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
        
