
import jwt
from config import settings

from django.conf import settings
from django.shortcuts import render, get_object_or_404
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField, SerializerMethodField

from foodiehotspots.models import Restaurant, Rate

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = 'HS256'

logger = settings.CUSTOM_LOGGER


class RestaurantSerializer(ModelSerializer):
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


class EvalCreateSerializers(ModelSerializer):
    
    eval_ids = SerializerMethodField()
    avg_score = SerializerMethodField()
    
    def get_eval_ids(self, obj):
        # 해당 식당의 평가 내역을 조회 할 수 있도록 (최신 순으로)
        evals = Rate.objects.filter(restaurant=self.context['view'].kwargs['pk']).order_by('-created_at')
        #value_list를 사용하면 object에서 지정해준 field값을 tuple형태로 return 해줍니다.
        evals_ids = evals.values_list('score','content','created_at')
        return evals_ids
    
    def get_avg_score(self, obj):
        return get_object_or_404(Restaurant, id=self.context['view'].kwargs['pk']).score
    
    #create함수는 modelSerializer에서 Model에 validate_data를 저장하기 위해 생성된 함수
    def create(self, validated_data):
        # 현재 요청을 보내는 사용자(user_id)를 추출
        token_str = self.context['request'].headers.get("Authorization").split(' ')[1]
        user_id = jwt.decode(token_str, SECRET_KEY, ALGORITHM)['user_id']
        # URL에서 rest_id 가져오기 (예: /api/restaurant/1/evaluation 에서 1을 추출)
        rest_id = self.context['view'].kwargs['pk']

        # 모델 생성 및 저장
        rate = Rate(
            user_id=user_id,
            restaurant_id=rest_id,
            score=validated_data['score'],
            content=validated_data['content']
        )
        rate.save()
        return rate
    # read_onl
    class Meta:
        model = Rate
        fields = ['score', 'content', 'avg_score', 'eval_ids']
        #읽기 전용 필드는 API 출력에 포함되지만 create 또는 update 조작 중 입력에 포함되면 안됩니다
        read_only_fields = ['avg_score', 'eval_ids']
        #write_only
        #이 값을 True로 설정하면 인스턴스를 업데이트하거나 만들때 필드가 사용될 수 있지만 표현을 serializer 할 때는 필드가 포함되지 않습니다
        #즉, 입력에는 사용하지만 Response할때는 return 하지 않습니다.
        extra_kwargs = {
            'score': {'write_only': True},
            'content': {'write_only': True}
        }
        
        
class FoodieDetailsSerializers(ModelSerializer):

    related_eval_ids = SerializerMethodField()
    
    
    def get_related_eval_ids(self, obj):
        # 해당 company_id로 지원한 지원공고인 recruit_id를 리스트로 반환
        # 해당 식당 평가 내역을 생성시간 역순(최신순) 으로 반환합니다.
        related_evals = Rate.objects.filter(restaurant=obj.id).order_by('-created_at')
        #value_list를 사용하면 object에서 지정해준 field값을 tuple형태로 return 해줍니다.
        evals_ids = related_evals.values_list('score','content','created_at')
        return evals_ids
    
    class Meta:
        model = Restaurant
        fields = '__all__'
        
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
