# my_app/tasks.py
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from django.db import models
from apscheduler.triggers.cron import CronTrigger
from foodiehotspots.views import test_scheduler
import time

scheduler = None #스케줄러 전역 변수로 설정

def start():
    scheduler = BackgroundScheduler()
    # DjangoJobStore : django 데이터베이스를 사용하여 스케쥴링 작업 저장 및 관리
    scheduler.add_jobstore(DjangoJobStore(), 'djangojobstore')

    register_events(scheduler)

    # 이전 스케줄이 완료될 때까지 대기할 시간(초) 설정
    '''
    @scheduler.scheduled_job('interval', seconds=5, name='test_scheduler', misfire_grace_time=wait_time)
        def auto_scheduler():
            test_scheduler()
    '''
    wait_time = 1000
    scheduler.add_job(test_scheduler(), 'interval', seconds=5, misfire_grace_time=wait_time)
    scheduler.start()
