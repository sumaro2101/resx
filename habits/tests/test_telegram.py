from django.test import TestCase
from django.utils import timezone

from django_celery_beat.models import CrontabSchedule

from datetime import datetime, date

from habits.services import construct_periodic, construct_time_to_task


class TestTelegram(TestCase):
    """Тесты касающиеся телеграма
    """    
