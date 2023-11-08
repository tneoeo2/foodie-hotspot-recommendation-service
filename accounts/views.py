import jwt
import time
import logging

from django.conf import settings
from django.core.cache import cache
from django.db.models.query import prefetch_related_objects
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

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

logger = logging.getLogger(__name__)

class UserDetailsView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserDetailUpdateSerializers
		
    # JWT 인증방식 클래스 지정하기
    authentication_classes = [JWTAuthentication]
    queryset = User.objects.all()

    def get_object(self, request):
        token_str = request.headers.get("Authorization").split(' ')[1]
        data = jwt.decode(token_str, SECRET_KEY, ALGORITHM)
        obj = get_object_or_404(User, id=data['user_id'])
        return obj

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object(request)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object(request)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        queryset = self.filter_queryset(self.get_queryset())
        if queryset._prefetch_related_lookups:
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance,
            # and then re-prefetch related objects
            instance._prefetched_objects_cache = {}
            prefetch_related_objects([instance], *queryset._prefetch_related_lookups)

        return Response(serializer.data)


class LocationListView(ListAPIView):  #캐싱 적용
    permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticated]
    
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
        start_time = time.time()
        location = cache.get('location')
        
        ## 저장은 serializer.data 즉 문자열로 했는데... dict로 나옴
        if location:
            logger.info(f'time_check: {time.time()-start_time}')
            return Response({"message": "this is testAPI", "data": location})
        else:
            serializer = LocationSerializers(Location.objects.get(id=1))
            print("seri:", serializer.data)
            print("seir type:", type(serializer.data))
            location = cache.set('location', serializer.data, timeout=20)
            logger.info(f'time_check: {time.time()-start_time}')
            return Response({"message": "this is testAPI", "data": serializer.data})
