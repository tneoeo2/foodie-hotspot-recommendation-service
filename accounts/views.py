import requests
import jwt 

from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from accounts.serializers import UserDetailUpdateSerializers, LocationSerializers
from accounts.models import Location
from utils.location import location_load

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
    permission_classes = (IsAuthenticated,)


    def get_object(self, request):
        token_str = request.headers.get("Authorization").split(' ')[1]
        data = jwt.decode(token_str, SECRET_KEY, ALGORITHM)
        return data['user_id']


class LocationListView(ListAPIView):
    permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticated]
    
    queryset = Location.objects.all()
    serializer_class = LocationSerializers
    
    def get_queryset(self):
        queryset = Location.objects.all()
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


class testAPI(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        # location_load.load_to_db()
        
        return Response({"message": "this is testAPI"})
        