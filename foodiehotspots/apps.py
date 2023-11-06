from django.apps import AppConfig
from django.conf import settings


class FoodiehotspotsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'foodiehotspots'

    def ready(self): #앱 초기화 및 설정
        if settings.SCHEDULER_DEFAULT:
            from foodiehotspots import tasks
            tasks.start()