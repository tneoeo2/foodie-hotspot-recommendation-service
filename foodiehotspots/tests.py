from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User
from foodiehotspots.models import Restaurant, Rate
from foodiehotspots.serializers import FoodieDetailsSerializers


BASE_URL = '/api/'

class FoodieDetailsViewTest(APITestCase):
    def setUp(self):
        # 테스트 데이터 생성
        self.restaurant = Restaurant.objects.create(
            sgg="인천시", name="김밥천국",
            longitude="37.12345", latitude="127.98765",
            # score=4.5,
        )
        # 캐시 데이터 생성
        cache.set(f'foodie_detail_{self.restaurant.pk}', {'sample_key': 'sample_value'}, 600)
        
        # 사용자 및 평가 데이터 생성
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        Rate.objects.create(user=self.user, restaurant=self.restaurant, score=4, content="리뷰 예시 1")
        Rate.objects.create(user=self.user, restaurant=self.restaurant, score=5, content="리뷰 예시 2")
        Rate.objects.create(user=self.user, restaurant=self.restaurant, score=4, content="리뷰 예시 3")

    def test_cache_hit(self):
        # 캐시 데이터가 있는 경우 -> 캐시 데이터 반환
        response = self.client.get(f'{BASE_URL}restaurant/{self.restaurant.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'sample_key': 'sample_value'})

    def test_cache_miss(self):
        cache.delete(f'foodie_detail_{self.restaurant.pk}')  # 캐시 삭제

        # 캐시 데이터가 없는 경우 -> DB에서 데이터 조회 후 캐시 생성
        response = self.client.get(f'{BASE_URL}restaurant/{self.restaurant.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], '김밥천국')

        # print(cache.get(f'foodie_detail_{self.restaurant.pk}'))
        self.assertIsNone(cache.get(f'foodie_detail_{self.restaurant.pk}'))  # 캐시 생성 안됨

    def test_caching_condition(self):
        cache.delete(f'foodie_detail_{self.restaurant.pk}')  # 캐시 삭제

        # 평가 데이터 2개 더 생성
        Rate.objects.create(user=self.user, restaurant=self.restaurant, score=4, content="리뷰 예시 4")
        Rate.objects.create(user=self.user, restaurant=self.restaurant, score=5, content="리뷰 예시 5")

        # 평점 4.0 이상, 평가가 5개 이상인 경우 -> 캐시 생성
        self.restaurant.score = 4.5
        self.restaurant.save()

        response = self.client.get(f'{BASE_URL}restaurant/{self.restaurant.pk}')
        self.assertEqual(response.status_code, 200)
        # print(cache.get(f'foodie_detail_{self.restaurant.pk}'))
        self.assertIsNotNone(cache.get(f'foodie_detail_{self.restaurant.pk}'))  # 캐시 생성 확인

    def test_caching_condition_not_met(self):
        cache.delete(f'foodie_detail_{self.restaurant.pk}')  # 캐시 삭제
        
        # 평점이 4.0 미만인 경우 -> 캐시 생성 안됨
        self.restaurant.score = 3.5
        self.restaurant.save()
        
        response = self.client.get(f'{BASE_URL}restaurant/{self.restaurant.pk}')
        self.assertEqual(response.status_code, 200)
        # print(response.data)
        self.assertIsNotNone(response.data)  # 데이터는 반환됨
        # print(cache.get(f'foodie_detail_{self.restaurant.pk}'))
        self.assertIsNone(cache.get(f'foodie_detail_{self.restaurant.pk}'))  # 캐시 생성 안됨

    def tearDown(self):
        User.objects.all().delete()
        Restaurant.objects.all().delete()
        Rate.objects.all().delete()