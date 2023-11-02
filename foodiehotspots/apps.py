from django.apps import AppConfig
from django.conf import settings


class FoodiehotspotsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'foodiehotspots'

    def ready(self):
        if settings.SCHEDULER_DEFAULT:
            from config import tasks
            tasks.start()