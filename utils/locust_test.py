from locust import HttpUser, task, between, TaskSet
from custom_logger import CustomLogger
import redis

logger = CustomLogger('INFO').get_logger()

class TestBehavior(TaskSet):
    '''
    Number of user : 최대 유저수
    Spawn rate : 한번에 유저가 생성되는 수
    Host : 서버주소
    
    Median : 응답 중간값
    Average : 평균
    Min : 최솟값
    
    '''
    @task
    def cache_location_data(self):
        # 주어진 엔드포인트로 GET 요청 보내기
        response = self.client.get("api/account/locations/")

        # 요청 및 응답에 대한 추가 작업 수행
        if response.status_code == 200:
            # 응답 성공 시 원하는 작업 수행
            pass
        else:
            # 에러 처리 또는 로깅
            logger.info("ERROR) 캐싱 url O")
    @task    
    def non_cache_location_data(self):
        # 주어진 엔드포인트로 GET 요청 보내기
        response = self.client.get("api/account/test/")

        # 요청 및 응답에 대한 추가 작업 수행
        if response.status_code == 200:
            # 응답 성공 시 원하는 작업 수행
            # logger.info("캐싱 url X")
            pass
        else:
            # 에러 처리 또는 로깅
            logger.error("ERROR) 캐싱 url X")
    

class LocustUser(HttpUser):
    host = 'http://127.0.0.1:8080/'  #! 호스트값 변경하여 사용할 것
    wait_time = between(1, 5)   #1~5초 사이 간격 랜덤 수행
    tasks = [TestBehavior]
    
    # def on_start(self):
    #     # 성능 테스트 시작 시 초기화 또는 설정
    # @task
    # def some_redis_operation(self):
    #     # Redis 연산 시나리오 작성
    #     r = redis.StrictRedis(host='localhost', port=6379, db=0)
    #     r.set('test_key', 'test_value')
    #     r.get('test_key')
