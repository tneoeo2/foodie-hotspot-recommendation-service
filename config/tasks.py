# my_app/tasks.py
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from django.db import models
from apscheduler.triggers.cron import CronTrigger

from foodiehotspots.views import test_scheduler
import time


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), 'djangojobstore')
    register_events(scheduler)

    
    @scheduler.scheduled_job('interval', seconds=5, name='auto_scheduler')
    def auto_scheduler():
        test_scheduler()

    scheduler.start()
