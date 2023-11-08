from django.shortcuts import render
from django.db.utils import IntegrityError
from django.conf import settings
from .models import Restaurant, Rate
from django.db.models import Count
from utils.get_data import processing_data
import logging
from rest_framework import status
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from  .serializers import RestaurantInfoUpdateSerializers, RestaurantSerializer

logger = settings.CUSTOM_LOGGER
# logger = logging.getLogger(__name__)


class RestaurantScheduler:
    
    def restaurant_scheduler(self):
        logger.info("식당정보 얻어오기 start---!")
        # self.processed_data = processing_data(page_index=3, page_size=5, total=50)
        self.processed_data = processing_data()
        # restaurant_data = Restaurant.objects.all()
        # serializer_class = RestaurantInfoUpdateSerializers(restaurant_data)
        self.save(self.processed_data)

    def save(self, data):    #데이터 저장    
        '''
        전처리된 데이터 저장 
            데이터의 형식은 다음과 같이 반환됩니다.
            #* [[{key : value}, {key : value}..{key : value}], [{{key : value}, {key : value}...{key : value}}]]
            #* list안에 list가 있고 그안에 dict가 존재
        
        1. uniqe 값으로 기존데이터에 값이 찾기 (name_address : 식당명+도로명주소)
            - 데이터가 존재하지않음 -> 데이터추가(save)
            - 기존 데이터가 존재 -> 데이터 비교후 변경점이 있다면 update
        '''
        processed_data = data
        # logger.info(f"self.processed_data----{processed_data}")
        data_list = processed_data
        queryset = Restaurant.objects.all()
        
        for data_el in data_list:
            # logger.info(f"data_list 형식 확인 : {data_list}")                
            for el in data_el: 
                name_address = ''
                name = el.get('name')  # 이 데이터에서 name_address 필드 추출
                address_lotno = el.get('address_lotno')  # 이 데이터에서 name_address 필드 추출
                address_roadnm = el.get('address_roadnm')  # 이 데이터에서 name_address 필드 추출
                
                #? 지번주소 없을시 도로명 주소로 탐색
                if address_lotno != None:
                    name_address =  f"{name} {address_lotno}"
                else: 
                    name_address = f"{name} {address_roadnm}"

                existing_data = queryset.filter(name_address=name_address).first()   #!왜 안나와..?
                serializer = RestaurantInfoUpdateSerializers(data=el)
                
                # print("-----------------------")
                # print("existing_data : ", existing_data)
                if existing_data != None:  #기존 데이터 존재 O
                    if serializer.is_valid():    
                        logger.debug(f'기존 데이터--- name_address :  {name_address}')
                        
                        serializer.update(existing_data, serializer.validated_data)
                else:               #기존 데이터 X
                    if serializer.is_valid():
                            new = serializer.validated_data.get('name')
                            logger.debug(f'신규데이터 추가--- {new}')
                            serializer.save()


class RestaurantCacheScheduler:
    serializer_class = RestaurantSerializer
    
    
    def get_rate_info(self, cnt):
        '''
        param: cnt 가져올 데이터의 수량 설정
        '''
        foodhotspots = 0
        # Restaurant별 평가 수 구하기
        rate_cnt = Rate.objects.annotate(rate_cnt=Count('restaurant'))
        for item in rate_cnt:
            logger.debug(f"Rate Count: {item.rate_cnt}")
        # 가장 많은 평가를 받은 Restaurant 가져오기
        top_rated_restaurants = rate_cnt.order_by('-rate_cnt')[:cnt]

        # 가장 많은 평가를 받은 Restaurant의 ID를 사용하여 Rate 가져오기
        foodhotspots = []
        if top_rated_restaurants:  
            for restaurant in list(top_rated_restaurants):
                restaurant_id = restaurant.restaurant_id
                foodhotspots.append(Restaurant.objects.get(id=restaurant_id))
                
            # logger.debug(f"foodhotspots: {foodhotspots[0].name}")
            return foodhotspots
        return foodhotspots    
    
    
    def set_foodhotspots(self):
        logger.info("-----맛집순위 캐싱-----")
        cnt = 100
        foodhotspots = self.get_rate_info(cnt)
        
        if foodhotspots !=  0: # 반환값 있을 때만 캐싱 진행
            cached_data = cache.get('foodhotspots')
        
            if cached_data is None:
                logger.info("-----기존 데이터 없음----")
                # cache.set('foodhotspots_encode', foodhotspots.encode("utf-8"))  # 데이터 인코딩 테스트(안되는듯?)
                cache.set('foodhotspots', foodhotspots)  
                logger.info(f'score 상위 식당 {cnt}개 캐싱 완료')
            
                return foodhotspots 