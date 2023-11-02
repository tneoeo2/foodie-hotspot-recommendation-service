from django.shortcuts import render
from django.conf import settings
logger = settings.CUSTOM_LOGGER


def test_scheduler():
    logger.debug('This is a debug message')
    logger.info('This is an info message')
    logger.error('This is an error message')
    print("test_scheduler!!!!!!!!")