from django.shortcuts import render
from rest_framework.generics import RetrieveUpdateAPIView
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from  .serializers import UserDetailUpdateSerializers

from django.shortcuts import get_object_or_404
import requests
from rest_framework_simplejwt.authentication import JWTAuthentication

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
    