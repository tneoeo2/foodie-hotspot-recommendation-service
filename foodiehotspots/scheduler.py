import math
import requests
import logging

from django.core.cache import cache
from django.conf import settings
from django.db.utils import IntegrityError
from django.db.models import Count

from .models import Restaurant, Rate
from utils.get_data import processing_data
from .serializers import RestaurantInfoUpdateSerializers, RestaurantSerializer

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


#discord-webhook으로도 사용
class DiscordWebHooksScheduler:
    
    def send_lunch_notification(self, user, rest_infos):
        #for all params, see https://discordapp.com/developers/docs/resources/webhook#execute-webhook
        headers = {
            'Content-Type': 'application/json',
            'Cookie': '__cfruid=b861bcb43f0e3e066010c80bbda0f4685b31ef00-1698971327; __dcfduid=4e92bafe772611eeafed66025b66c56b; __sdcfduid=4e92bafe772611eeafed66025b66c56bb9116c38b61ecd811cf74f8dd52d6bed962e9d6126195927285a8f19cf4d3584; _cfuvid=IbG2yMM4vRp1X3cRolIUmKgcDlRjIwnsrhuGQu1m3Ok-1698971327328-0-604800000'
                    }
        data = {
            "username": "LunchHere",
            "avatar_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRN9lF93jsUSQ2J5jX4f4OcOvJf4I37mCdrfg&usqp=CAU",
            "content" : "Your LunchHere! {}님 오늘의 점심 추천 맛집은~".format(user.username),
            "embeds" : [
                
            ]
        }
        
        for rest_info in rest_infos[:5]:
            #leave this out if you dont want an embed
            #for all params, see https://discordapp.com/developers/docs/resources/channel#embed-object
            data["embeds"].append(
                {
                "author": {
                    "name": rest_info[1].name,
                    },
                "description":rest_info[1].food_category,
                "fields": [
                        {
                            "name": "지번",
                            "value": rest_info[1].address_lotno
                        },
                        {
                            "name": "도로명",
                            "value": rest_info[1].address_roadnm
                        },
                    ],
                "footer": {
                    "text": "언제나 당신을 위한 맛집과 함께 돌아올게요, Enjoy your LunchHere :)",
                    "icon_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRN9lF93jsUSQ2J5jX4f4OcOvJf4I37mCdrfg&usqp=CAU"
                    }  
                }
            )
        data["embeds"].append(
                {
                "author": {
                    "name": "Webhook Information",
                    "icon_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRkkqaddbEgITDj4ScVsIi1wRND2Z4g1nUm_w&usqp=CAU"
                },
                "color": 6815584,
                "fields": [
                    {
                        "name": "여러분 팀의 Webhook URL",
                        "value": "https://discord.com/api/webhooks/1168538153775280138/kIRP6uWMpvlN1cpv-RXKH69ZmiCtPK1hkVpsp7K12rAZAqQ0lgqyetPjDfAOTP3S3Iko"
                    },
                    {
                        "name": "discord-webhooks-guide",
                        "value": "https://birdie0.github.io/discord-webhooks-guide/index.html"
                    },
                    {
                        "name": "get decimal color",
                        "value": "https://html-color.org/67ff60 , Discord Webhook color use '\''Decimal'\'' value, search your color in this site\n ex) #67ff60 > 6815584"
                    }
                ]
            }
        )
        
        url = "https://discord.com/api/webhooks/1169806092138717267/57BBLDa6dr6GgE3p9U2humk-xHQmz1mJQNWUktYDIqUIsqmu5TH8ViQcF7HzcGaD-GQx" #webhook url, from here: https://i.imgur.com/f9XnAew.png
        
        # print(json.dumps(data))
        result = requests.post(url,  headers=headers,  data=json.dumps(data))

        try:
            result.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        else:
            print("Payload delivered successfully, code {}.".format(result.status_code))
    
    def get_lunch_list(self, user, radius=0.5):
        user_point = (float(user.longitude),  float(user.latitude))
        
        restaurants = Restaurant.objects.all().order_by('-score')
        rest_infos = set()
        
        while len(rest_infos) <= 5:
            for restaurant in restaurants:
                rest_point = (float(restaurant.longitude), float(restaurant.latitude))
                distance = self.lat_lon_to_km(user_point, rest_point)
                if distance <= radius and (distance, restaurant) not in rest_infos:
                    rest_infos.add((distance, restaurant))
            radius += 0.5
            
        rest_infos = list(rest_infos)
        rest_infos.sort(key=lambda x : x[0])
        
        return rest_infos
    
    def recommend_lunch(self):
        #현재 추천 시스템을 받는 모든 사용자의 onject를 return 
        user_instance = User.objects.all().filter(is_recommend=True)
        
        
        #현재 사용자 반경 안에 있는 식당 중에 평점이 넢은 순서대로 나열
        
        #5개가 안되면 계속해서 반경을 늘려가도록 합니다.
        #제공 하고자하는 메뉴의 종류는 분식, 일식, 중식, 패스트푸드
        for obj in user_instance:
            rest_infos = self.get_lunch_list(obj)
            self.send_lunch_notification(obj, rest_infos)
            
                
    #해당 user의 일정 범위에 있는 맛집을 return 해줍니다.
    def lat_lon_to_km(self, point_1, point_2):
        lat1 = point_1[1]
        lon1 = point_1[0]
        lat2 = point_2[1]
        lon2 = point_2[0]

        # R = 6371  # km
        R = 1  # km
        dLat = math.radians(lat2-lat1)
        dLon = math.radians(lon2-lon1)

        lat1 = math.radians(lat1)
        lat2 = math.radians(lat2)

        a = math.sin(dLat/2) * math.sin(dLat/2) + \
            math.sin(dLon/2) * math.sin(dLon/2) * math.cos(lat1) * math.cos(lat2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        return R * c 
    
    
# class RestaurantCacheScheduler:
#     serializer_class = RestaurantSerializer
    
    
#     def get_rate_info(self, cnt):
#         '''
#         param: cnt 가져올 데이터의 수량 설정
#         '''
#         foodhotspots = 0
#         # Restaurant별 평가 수 구하기
#         rate_cnt = Rate.objects.annotate(rate_cnt=Count('restaurant'))
#         for item in rate_cnt:
#             logger.debug(f"Rate Count: {item.rate_cnt}")
#         # 가장 많은 평가를 받은 Restaurant 가져오기
#         top_rated_restaurants = rate_cnt.order_by('-rate_cnt')[:cnt]

#         # 가장 많은 평가를 받은 Restaurant의 ID를 사용하여 Rate 가져오기
#         foodhotspots = []
#         if top_rated_restaurants:  
#             for restaurant in list(top_rated_restaurants):
#                 restaurant_id = restaurant.restaurant_id
#                 foodhotspots.append(Restaurant.objects.get(id=restaurant_id))
                
#             # logger.debug(f"foodhotspots: {foodhotspots[0].name}")
#             return foodhotspots
#         return foodhotspots    
    
    
#     def set_foodhotspots(self):
#         logger.info("-----맛집순위 캐싱-----")
#         cnt = 100
#         foodhotspots = self.get_rate_info(cnt)
        
#         if foodhotspots !=  0: # 반환값 있을 때만 캐싱 진행
#             cached_data = cache.get('foodhotspots')
        
#             if cached_data is None:
#                 logger.info("-----기존 데이터 없음----")
#                 # cache.set('foodhotspots_encode', foodhotspots.encode("utf-8"))  # 데이터 인코딩 테스트(안되는듯?)
#                 cache.set('foodhotspots', foodhotspots)  
#                 logger.info(f'score 상위 식당 {cnt}개 캐싱 완료')
            
#                 return foodhotspots 