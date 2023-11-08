from django.shortcuts import render
from rest_framework.generics import RetrieveUpdateAPIView
from django.shortcuts import render
from django.core.cache import cache
from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView
from django.conf import settings
from .models import Location
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from  .serializers import UserDetailUpdateSerializers, LocationSerializers
from django.shortcuts import get_object_or_404
import requests
import logging
import jwt 

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = 'HS256'


# Create your views here.
class UserDetailsView(RetrieveUpdateAPIView):
    """
    Reads and updates UserModel fields
    Accepts GET, PUT, PATCH methods.

    Default accepted fields: username, first_name, last_name
    Default display fields: pk, username, email, first_name, last_name
    Read-only fields: pk, email

    Returns UserModel fields.
    """
    serializer_class = UserDetailUpdateSerializers
    permission_classes = [IsAuthenticated]
		
    # JWT 인증방식 클래스 지정하기
    authentication_classes = [JWTAuthentication]


    def get_object(self, request):
        token_str = request.headers.get("Authorization").split(' ')[1]
        data = jwt.decode(token_str, SECRET_KEY, ALGORITHM)
        obj = get_object_or_404(User, id=data['user_id'])
        return obj
    



class LocationListView(ListAPIView):  #캐싱 적용
    permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticated]
    
    # queryset = Location.objects.all()
    queryset = cache.get('locations')
    if queryset is None:
        queryset = Location.objects.all()
    # queryset = Location.objects.all()
    queryset = cache.get('locations')
    if queryset is None:
        queryset = Location.objects.all()
    serializer_class = LocationSerializers
    
    def get_queryset(self):
        # queryset = Location.objects.all()
        queryset = cache.get('locations')
        if queryset is None:
            queryset = Location.objects.all()
            cache.set('locations', queryset)
        # queryset = Location.objects.all()
        queryset = cache.get('locations')
        if queryset is None:
            queryset = Location.objects.all()
            cache.set('locations', queryset)
        query_params = self.request.query_params
        if not query_params:
            return queryset
        
        do_si = query_params.get("do_si", None)
        if do_si:
            queryset = queryset.filter(dosi=do_si)
        
        sgg = query_params.get("sgg", None)
        if sgg:
            queryset = queryset.filter(sgg=sgg)
        
        return queryset


# class testAPI(APIView):
#     permission_classes = [AllowAny]
# class testAPI(APIView):
#     permission_classes = [AllowAny]
    
#     def get(self, request):
#         # location_load.load_to_db()
#     def get(self, request):
#         # location_load.load_to_db()
        
#         return Response({"message": "this is testAPI"})
#         return Response({"message": "this is testAPI"})

# class testAPI(ListAPIView):    #캐싱 적용 안됨
#     permission_classes = [AllowAny]
    
#     queryset = Location.objects.all()
#     serializer_class = LocationSerializers
    
#     def get_queryset(self):
#         queryset = Location.objects.all()
#         query_params = self.request.query_params
#         if not query_params:
#             return queryset
        
#         do_si = query_params.get("do_si", None)
#         if do_si:
#             queryset = queryset.filter(dosi=do_si)
        
#         sgg = query_params.get("sgg", None)
#         if sgg:
#             queryset = queryset.filter(sgg=sgg)
        
#         return queryset
# class testAPI(ListAPIView):    #캐싱 적용 안됨
#     permission_classes = [AllowAny]
    
#     queryset = Location.objects.all()
#     serializer_class = LocationSerializers
    
#     def get_queryset(self):
#         queryset = Location.objects.all()
#         query_params = self.request.query_params
#         if not query_params:
#             return queryset
        
#         do_si = query_params.get("do_si", None)
#         if do_si:
#             queryset = queryset.filter(dosi=do_si)
        
#         sgg = query_params.get("sgg", None)
#         if sgg:
#             queryset = queryset.filter(sgg=sgg)
        
#         return queryset
