import math

from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ParseError
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework import status

from foodiehotspots.models import Restaurant
from foodiehotspots.serializers import RestaurantSerializer


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
            print(distance)
            if distance <= radius:
                within_radius.append((distance, r))
        print(within_radius)

        sorted_restaurants = []

        try:
            for i in range(len(within_radius)):
                distance, r = within_radius[i]
                sorted_restaurants.append({"distance": distance, "restaurant_id": r.id})
        except IndexError:
            # 예외 처리 로직 추가
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

        # serializer = RestaurantSerializer(sorted_restaurant, many=True)
        # return Response(
        #     serializer.data,
        #     status=status.HTTP_200_OK,
        # )

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

