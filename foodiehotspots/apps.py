from django.apps import AppConfig
from django.conf import settings
import os

class FoodiehotspotsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'foodiehotspots'

    def ready(self): #앱 초기화 및 설정
        if os.environ.get('RUN_MAIN', None) is not None:
            if settings.SCHEDULER_DEFAULT:
                from foodiehotspots import tasks
                tasks.start()
                tasks.schedule_process()