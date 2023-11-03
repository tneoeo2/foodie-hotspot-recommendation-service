import math

from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ParseError

from foodiehotspots.models import Restaurant
from foodiehotspots.serializers import RestaurantSerializer


class RestaurantList(ListAPIView):
    '''
    GET /api/restaurant/?lat=37.4&lon=127.08
    GET /api/restaurant/?lat=37.4&lon=127.08&radius=3.0&sorting=score
    '''
    permissions_classes = [AllowAny]

    serializer_class = RestaurantSerializer
    # pagination_class = LimitOffsetPagination

    def get_queryset(self):
        lat = self.request.query_params.get('lat')
        lon = self.request.query_params.get('lon')
        radius = self.request.query_params.get('radius', 1.0)
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

        try:
            for i in range(len(within_radius)):
                distance, r = within_radius[i]
        except IndexError:
            # 예외 처리 로직 추가
            print("인덱스가 범위를 벗어났습니다.")

        # 거리 순 정렬
        if sorting == 'distance':
            within_radius.sort(key=lambda x: x[0])
            sorted_distance_restaurant = [r[1] for r in within_radius]

            print("레스토랑을 거리 순으로 정렬했습니다:")
            for restaurant in sorted_distance_restaurant:
                print(f"레스토랑 ID: {restaurant.id}, 거리: {within_radius[restaurant.id-1][0]} km")

            return sorted_distance_restaurant
        
        # score 내림차순 정렬
        elif sorting == 'score':
            within_radius.sort(key=lambda x: x[1].score, reverse=True)
            sorted_score_restaurant = [r[1] for r in within_radius]

            print("레스토랑을 평점(score) 순으로 내림차순 정렬했습니다:")
            for restaurant in sorted_score_restaurant:
                print(f"레스토랑 ID: {restaurant.id}, 평점(score): {restaurant.score}")

            return sorted_score_restaurant
        else:
            raise ParseError()
        
    # def get_serializer_context(self):
    #     context = super().get_serializer_context()
    #     context['user_point'] = self.user_point  # 사용자 중심점을 serializer에 전달
    #     return self.serializer_class(context=context)


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

