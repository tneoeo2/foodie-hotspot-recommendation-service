import jwt
import requests
from django.shortcuts import render, get_object_or_404
import math
import json
from rest_framework import mixins, status
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import FoodieDetailsSerializers, EvalCreateSerializers
from .models import Restaurant, Rate
from .serializers import RestaurantInfoUpdateSerializers
from utils.get_data import processing_data
from accounts.models import User

from config import settings

logger = settings.CUSTOM_LOGGER

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = 'HS256'

# Create your views here.
class FoodieDetailsView(mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                            GenericAPIView):
    serializer_class = FoodieDetailsSerializers
    permission_classes = [IsAuthenticated]
		
    # JWT 인증방식 클래스 지정하기
    authentication_classes = [JWTAuthentication]
    queryset = Restaurant.objects.all()
    
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        return obj
    
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

class EvalCreateView(mixins.CreateModelMixin,
                      GenericAPIView):
    serializer_class = EvalCreateSerializers
    permission_classes = [IsAuthenticated]
		
    # JWT 인증방식 클래스 지정하기
    authentication_classes = [JWTAuthentication]
    
    
    #1. 현재 음식점의 obj를 불러와 해당 score을 업데이트
    def create(self, request, *args, **kwargs):
        
        # 평가 가 생성되면, 해당 맛집의 평점 을 업데이트 한다.
        # 평균 계산하여 업데이트
        pk = self.kwargs.get('pk')
        instance = get_object_or_404(Restaurant, id=pk)
        instance.score = (instance.score + int(request.data.get('score'))) / 2
        instance.save()
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    
    #2. 함께 들어온 'score'와 'content'가 user_id와 content_id가 같이 들어가야함
    def get_object(self, request):
        token_str = request.headers.get("Authorization").split(' ')[1]
        data = jwt.decode(token_str, SECRET_KEY, ALGORITHM)
        obj = get_object_or_404(Rate, user=data['user_id'])
        return obj
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class RestaurantScheduler:
    
    def restaurant_scheduler(self):
        logger.info("식당정보 얻어오기 start---!")
        self.processed_data = processing_data()
        self.save(self.processed_data)

    def save(self, data):    #데이터 저장    
        '''
        전처리된 데이터 저장 
            데이터의 형식은 다음과 같이 반환됩니다.
            #* [[{key : value}, {key : value}..{key : value}], [{{key : value}, {key : value}...{key : value}}]]
            #* list안에 list가 있고 그안에 dict가 존재
        
        '''
        processed_data = data
        data_list = processed_data
        queryset = Restaurant.objects.all()
        
        for data_el in data_list:
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
                
                if existing_data != None:  #기존 데이터 존재 O
                    if serializer.is_valid():    
                        
                        serializer.update(existing_data, serializer.validated_data)
                else:               #기존 데이터 X
                    if serializer.is_valid():
                            new = serializer.validated_data.get('name')
                            serializer.save()
#discord-webhook으로도 사용
class DiscordWebHooks:
    
    def food_list(self):
        #현재 추천 시스템을 받는 모든 사용자의 onject를 return 
        user_instance = User.objects.all().filter(is_recommend=True)
        
        #현재 사용자 반경 안에 있는 식당 중에 평점이 넢은 순서대로 나열
        
        #5개가 안되면 계속해서 반경을 늘려가도록 합니다.
        #제공 하고자하는 메뉴의 종류는 분식, 일식, 중식, 패스트푸드
        for obj in user_instance:
            user_point = (float(obj.longitude),  float(obj.latitude))
            
            default_radius = 0.5
            
            restaurants = Restaurant.objects.all().order_by('-score')
            rest_infos = []
            
            while len(rest_infos) <= 5:
                for restaurant in restaurants:
                    rest_point = (float(restaurant.longitude), float(restaurant.latitude))
                    distance = self.lat_lon_to_km(user_point, rest_point)
                    if distance <= default_radius:
                        rest_infos.append((distance, restaurant))
                default_radius += 0.5
            
            rest_infos.sort(key=lambda x : x[0])
            
            #for all params, see https://discordapp.com/developers/docs/resources/webhook#execute-webhook
            headers = {
                'Content-Type': 'application/json',
                'Cookie': '__cfruid=b861bcb43f0e3e066010c80bbda0f4685b31ef00-1698971327; __dcfduid=4e92bafe772611eeafed66025b66c56b; __sdcfduid=4e92bafe772611eeafed66025b66c56bb9116c38b61ecd811cf74f8dd52d6bed962e9d6126195927285a8f19cf4d3584; _cfuvid=IbG2yMM4vRp1X3cRolIUmKgcDlRjIwnsrhuGQu1m3Ok-1698971327328-0-604800000'
                       }
            data = {
                "username": "LunchHere",
                "avatar_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRN9lF93jsUSQ2J5jX4f4OcOvJf4I37mCdrfg&usqp=CAU",
                "content" : "Your LunchHere! {}님 오늘의 점심 추천 맛집은~".format(obj.username),
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
            
            print(json.dumps(data))
            result = requests.post(url,  headers=headers,  data=json.dumps(data))

            try:
                result.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print(err)
            else:
                print("Payload delivered successfully, code {}.".format(result.status_code))
                
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
