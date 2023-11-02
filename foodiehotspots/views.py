from django.shortcuts import render
from django.conf import settings
from utils.get_data import processing_data

logger = settings.CUSTOM_LOGGER

processed_data = ''

def test_scheduler():
    logger.info("식당정보 얻어오기 start---!")
    processed_data = processing_data()