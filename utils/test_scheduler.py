from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
logger = settings.CUSTOM_LOGGER


scheduler = BackgroundScheduler()

def my_job():
    print("Scheduled job is running!")

scheduler.add_job(my_job, 'interval', seconds=5)

scheduler.start()

# 애플리케이션이 계속 실행되도록 대기
try:
    while True:
        pass
except (KeyboardInterrupt, SystemExit):
    # Ctrl+C 또는 애플리케이션 종료 신호를 받으면 스케줄러를 종료하고 프로그램 종료
    scheduler.shutdown()
