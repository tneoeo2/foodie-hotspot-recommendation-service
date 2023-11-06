import jwt

from django.shortcuts import render, get_object_or_404

from rest_framework import mixins, status
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import FoodieDetailsSerializers, EvalCreateSerializers
from .models import Restaurant, Rate
from .serializers import RestaurantInfoUpdateSerializers
from utils.get_data import processing_data

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
                                  
