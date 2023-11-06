from functools import partial
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from django.db import models
from apscheduler.triggers.cron import CronTrigger
from foodiehotspots.views import RestaurantScheduler, DiscordWebHooks
import time

scheduler = None #스케줄러 전역 변수로 설정

def start():
    scheduler = BackgroundScheduler()
    # DjangoJobStore : django 데이터베이스를 사용하여 스케쥴링 작업 저장 및 관리
    scheduler.add_jobstore(DjangoJobStore(), 'djangojobstore')
    register_events(scheduler)
    # 이전 스케줄이 완료될 때까지 대기할 시간(초) 설정
    wait_time = 1000
    job1 = partial(RestaurantScheduler.restaurant_scheduler, RestaurantScheduler())
    scheduler.add_job(job1, 'cron',hour=2,misfire_grace_time=wait_time) 
    # scheduler.add_job(job1, 'cron',minutes='0',misfire_grace_time=wait_time) #!매분 실행으로 테스트
    scheduler.start()
    
def schedule_process():
    scheduler = BackgroundScheduler()
    job2 = partial(DiscordWebHooks.food_list, DiscordWebHooks())
    #점심시간 30분전 식당 추천
    scheduler.add_job(job2, 'cron', hour=11, minute=30)
    scheduler.start()
