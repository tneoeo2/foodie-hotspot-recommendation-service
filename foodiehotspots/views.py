import math
import jwt
from utils.get_data import processing_data
from config import settings

from django.shortcuts import render, get_object_or_404
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ParseError
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.authentication import JWTAuthentication

from foodiehotspots.models import Restaurant, Rate
from foodiehotspots.serializers import RestaurantSerializer, RestaurantInfoUpdateSerializers, FoodieDetailsSerializers, EvalCreateSerializers

logger = settings.CUSTOM_LOGGER

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = 'HS256'


class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'


class RestaurantList(ListAPIView):
    '''
    GET /api/restaurant/?lat=37.4&lon=127.08
    GET /api/restaurant/?lat=37.4&lon=127.08&radius=3.0&sorting=score
    '''
    permissions_classes = [AllowAny]

    serializer_class = RestaurantSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        lat = self.request.query_params.get('lat')
        lon = self.request.query_params.get('lon')
        radius = self.request.query_params.get('radius', 1.1)
        sorting = self.request.query_params.get('sorting', 'distance')  # 'distance' or 'score'

        user_point = (float(lat), float(lon))

        # 주어진 범위 안에 있는 식당 리스트
        within_radius = []
        all_restaurants = Restaurant.objects.all()

        for r in all_restaurants:
            restaurant_point = (float(r.longitude), float(r.latitude))
            distance = lat_lon_to_km(user_point, restaurant_point)
            if distance <= radius:
                within_radius.append((distance, r))

        sorted_restaurants = []

        try:
            for i in range(len(within_radius)):
                distance, r = within_radius[i]
                sorted_restaurants.append({"distance": distance, "restaurant_id": r.id})
        except IndexError:
            raise ValueError(detail="인덱스가 범위를 벗어났습니다.")

        # 거리 순 정렬
        if sorting == 'distance':
            within_radius.sort(key=lambda x: x[0])
            sorted_restaurant = [r[1] for r in within_radius]  # sorted_distance_restaurant
        
        # score 내림차순 정렬
        elif sorting == 'score':
            within_radius.sort(key=lambda x: x[1].score, reverse=True)
            sorted_restaurant = [r[1] for r in within_radius]  # sorted_score_restaurant
        else:
            raise ParseError()
        
        return sorted_restaurant

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


def lat_lon_to_km(point_1, point_2):
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
