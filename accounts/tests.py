from rest_framework.test import APITestCase
from django.core.cache import cache
from accounts.models import Location
from accounts.serializers import LocationSerializers


BASE_URL = '/api/'

class LocationListViewTest(APITestCase):
    def setUp(self):
        # 테스트 데이터 생성
        Location.objects.create(dosi="Seoul", sgg="Gangnam")
        Location.objects.create(dosi="Seoul", sgg="Mapo")

    def test_caching(self):
        # 캐시에 데이터가 없는 경우 API를 호출하고 데이터를 캐시에 저장
        response = self.client.get(f'{BASE_URL}account/locations/', {'dosi': 'Seoul'})
        self.assertEqual(response.status_code, 200)

        # 캐싱 응답 되는지 확인
        cached_response = self.client.get(f'{BASE_URL}account/locations/', {'dosi': 'Seoul'})
        self.assertEqual(response.data, cached_response.data)

        # 캐시에 데이터가 있는 경우 캐시된 데이터를 반환
        cached_data = cache.get('location_data')
        self.assertIsNotNone(cached_data)

        # LocationSerializers로 데이터 직렬화하여 캐시된 데이터와 비교
        queryset = Location.objects.filter(dosi="Seoul")
        serializer = LocationSerializers(queryset, many=True)
        self.assertEqual(cached_data, serializer.data)

    def tearDown(self):
        Location.objects.all().delete()