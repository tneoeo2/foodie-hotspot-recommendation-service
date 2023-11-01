from django.shortcuts import render
from rest_framework.generics import RetrieveUpdateAPIView
from django.conf import settings
from django.contrib.auth import get_user_model
from .app_settings import api_settings
from rest_framework.permissions import AllowAny, IsAuthenticated
from  .serializers import UserDetailUpdateSerializers
from django.shortcuts import get_object_or_404
import requests

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
    permission_classes = (IsAuthenticated,)


    def get_object(self):
        return self.request.user
    
    def get_queryset(self,data):
        """
        Adding this method since it is sometimes called when using
        django-rest-swagger
        """
        instance = get_object_or_404(get_user_model(), id=data['user_id'])
        
        return instance
    
    """
    Concrete view for retrieving, updating a model instance.
    """
    def get(self, request, *args, **kwargs):
        
        token_str = request.headers.get("Authorization").split(' ')[1]
        data = jwt.decode(token_str, SECRET_KEY, ALGORITHM)
        
        instance = self.get_queryset(data)
        
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        
        token_str = request.headers.get("Authorization").split(' ')[1]
        data = jwt.decode(token_str, SECRET_KEY, ALGORITHM)
        
        instance = self.get_queryset(data)
        
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        
        token_str = request.headers.get("Authorization").split(' ')[1]
        data = jwt.decode(token_str, SECRET_KEY, ALGORITHM)
        
        instance = self.get_queryset(data)
        
        return self.partial_update(request, *args, **kwargs)