import jwt

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.serializers import UserDetailUpdateSerializers, LocationSerializers
from accounts.models import User, Location
from utils.location import location_load


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = 'HS256'


class UserDetailsView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserDetailUpdateSerializers
		
    # JWT 인증방식 클래스 지정하기
    authentication_classes = [JWTAuthentication]


    def get_object(self, request):
        token_str = request.headers.get("Authorization").split(' ')[1]
        data = jwt.decode(token_str, SECRET_KEY, ALGORITHM)
        obj = get_object_or_404(User, id=data['user_id'])
        return obj


# class LocationListView(ListAPIView):
#     permission_classes = [AllowAny]
#     # permission_classes = [IsAuthenticated]

#     serializer_class = LocationSerializers
    
#     def get_queryset(self):
#         # 시도 및 시군구 목록을 캐시에서 가져오기
#         cached_data = cache.get('location_data')
#         if cached_data:
#             print(cached_data)
#             return cached_data

#         queryset = Location.objects.all()
#         query_params = self.request.query_params
#         if not query_params:
#             return queryset
        
#         do_si = query_params.get("dosi", None)
#         if do_si:
#             queryset = queryset.filter(dosi=do_si)
        
#         sgg = query_params.get("sgg", None)
#         if sgg:
#             queryset = queryset.filter(sgg=sgg)
        
#         # 데이터를 캐시에 저장하고 반환
#         cache.set('location_data', queryset)
        
#         return queryset


class LocationListView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        # 시도 및 시군구 목록을 캐시에서 검색
        cached_data = cache.get('location_data')
        if cached_data is not None:
            return Response(cached_data)  # set() 으로 저장할 때 이미 serializer화 된 상태로 저장됨
        

        do_si = request.query_params.get("dosi", None)
        sgg = request.query_params.get("sgg", None)

        if do_si:
            filtered_objects = Location.objects.filter(dosi=do_si)
        elif sgg:
            filtered_objects = Location.objects.filter(sgg=sgg)
        else:
            filtered_objects = Location.objects.all()

        serializer = LocationSerializers(filtered_objects, many=True)

        # 데이터를 캐시에 저장 (무기한 유지)
        cache.set('location_data', serializer.data)

        return Response(serializer.data)


class testAPI(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        # location_load.load_to_db()
        
        return Response({"message": "this is testAPI"})