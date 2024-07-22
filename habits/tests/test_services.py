from datetime import date, datetime

from django.utils import timezone

from rest_framework.test import APITestCase

from django_celery_beat.models import CrontabSchedule

from habits.services import (construct_time_to_task,
                             construct_periodic,
                             )


class TestServices(APITestCase):
    """Тест сервисов
    """

    def test_construct_petiodic(self):
        """Тест конструктора периодичности
        """
        self.assertEqual(
            construct_periodic('*', '*', '*/1'),
            'Каждый день',
            )
        self.assertEqual(
            construct_periodic('*', '*', '*/2'),
            'Каждые 2 дня',
            )
        self.assertEqual(
            construct_periodic('*', '*', '*/3'),
            'Каждые 3 дня',
            )
        self.assertEqual(
            construct_periodic('*', '*', '*/4'),
            'Каждые 4 дня',
            )
        self.assertEqual(
            construct_periodic('*', '*', '*/5'),
            'Каждые 5 дней',
            )
        self.assertEqual(
            construct_periodic('*', '*', '*/6'),
            'Каждые 6 дней',
            )
        self.assertEqual(
            construct_periodic('*', '*', '*/7'),
            'Каждые 7 дней',
            )
        self.assertEqual(
            construct_periodic('*', '*/1', '*'),
            'Каждый час',
            )
        self.assertEqual(
            construct_periodic('*', '*/2', '*'),
            'Каждые 2 часа',
            )
        self.assertEqual(
            construct_periodic('*', '*/3', '*'),
            'Каждые 3 часа',
            )
        self.assertEqual(
            construct_periodic('*', '*/4', '*'),
            'Каждые 4 часа',
            )
        self.assertEqual(
            construct_periodic('*', '*/5', '*'),
            'Каждые 5 часов',
            )
        self.assertEqual(
            construct_periodic('*', '*/6', '*'),
            'Каждые 6 часов',
            )
        self.assertEqual(
            construct_periodic('*', '*/7', '*'),
            'Каждые 7 часов',
            )
        self.assertEqual(
            construct_periodic('*', '*/8', '*'),
            'Каждые 8 часов',
            )
        self.assertEqual(
            construct_periodic('*', '*/9', '*'),
            'Каждые 9 часов',
            )
        self.assertEqual(
            construct_periodic('*', '*/10', '*'),
            'Каждые 10 часов',
            )
        self.assertEqual(
            construct_periodic('*', '*/11', '*'),
            'Каждые 11 часов',
            )
        self.assertEqual(
            construct_periodic('*', '*/12', '*'),
            'Каждые 12 часов',
            )
        self.assertEqual(
            construct_periodic('*', '*/13', '*'),
            'Каждые 13 часов',
            )
        self.assertEqual(
            construct_periodic('*', '*/14', '*'),
            'Каждые 14 часов',
            )
        self.assertEqual(
            construct_periodic('*', '*/15', '*'),
            'Каждые 15 часов',
            )
        self.assertEqual(
            construct_periodic('*', '*/16', '*'),
            'Каждые 16 часов',
            )
        self.assertEqual(
            construct_periodic('*', '*/17', '*'),
            'Каждые 17 часов',
            )
        self.assertEqual(
            construct_periodic('*', '*/18', '*'),
            'Каждые 18 часов',
            )
        self.assertEqual(
            construct_periodic('*', '*/19', '*'),
            'Каждые 19 часов',
            )
        self.assertEqual(
            construct_periodic('*', '*/20', '*'),
            'Каждые 20 часов',
            )
        self.assertEqual(
            construct_periodic('*', '*/21', '*'),
            'Каждый 21 час',
            )
        self.assertEqual(
            construct_periodic('*', '*/22', '*'),
            'Каждые 22 часа',
            )
        self.assertEqual(
            construct_periodic('*', '*/23', '*'),
            'Каждые 23 часа',
            )
        self.assertEqual(
            construct_periodic('*/1', '*', '*'),
            'Каждую минуту',
            )
        self.assertEqual(
            construct_periodic('*/2', '*', '*'),
            'Каждые 2 минуты',
            )
        self.assertEqual(
            construct_periodic('*/3', '*', '*'),
            'Каждые 3 минуты',
            )
        self.assertEqual(
            construct_periodic('*/4', '*', '*'),
            'Каждые 4 минуты',
            )
        self.assertEqual(
            construct_periodic('*/5', '*', '*'),
            'Каждые 5 минут',
            )
        self.assertEqual(
            construct_periodic('*/6', '*', '*'),
            'Каждые 6 минут',
            )
        self.assertEqual(
            construct_periodic('*/7', '*', '*'),
            'Каждые 7 минут',
            )
        self.assertEqual(
            construct_periodic('*/8', '*', '*'),
            'Каждые 8 минут',
            )
        self.assertEqual(
            construct_periodic('*/9', '*', '*'),
            'Каждые 9 минут',
            )
        self.assertEqual(
            construct_periodic('*/10', '*', '*'),
            'Каждые 10 минут',
            )
        self.assertEqual(
            construct_periodic('*/11', '*', '*'),
            'Каждые 11 минут',
            )
        self.assertEqual(
            construct_periodic('*/12', '*', '*'),
            'Каждые 12 минут',
            )
        self.assertEqual(
            construct_periodic('*/13', '*', '*'),
            'Каждые 13 минут',
            )
        self.assertEqual(
            construct_periodic('*/14', '*', '*'),
            'Каждые 14 минут',
            )
        self.assertEqual(
            construct_periodic('*/15', '*', '*'),
            'Каждые 15 минут',
            )
        self.assertEqual(
            construct_periodic('*/16', '*', '*'),
            'Каждые 16 минут',
            )
        self.assertEqual(
            construct_periodic('*/17', '*', '*'),
            'Каждые 17 минут',
            )
        self.assertEqual(
            construct_periodic('*/18', '*', '*'),
            'Каждые 18 минут',
            )
        self.assertEqual(
            construct_periodic('*/19', '*', '*'),
            'Каждые 19 минут',
            )
        self.assertEqual(
            construct_periodic('*/20', '*', '*'),
            'Каждые 20 минут',
            )
        self.assertEqual(
            construct_periodic('*/21', '*', '*'),
            'Каждую 21 минуту',
            )
        self.assertEqual(
            construct_periodic('*/22', '*', '*'),
            'Каждые 22 минуты',
            )
        self.assertEqual(
            construct_periodic('*/23', '*', '*'),
            'Каждые 23 минуты',
            )
        self.assertEqual(
            construct_periodic('*/24', '*', '*'),
            'Каждые 24 минуты',
            )
        self.assertEqual(
            construct_periodic('*/25', '*', '*'),
            'Каждые 25 минут',
            )
        self.assertEqual(
            construct_periodic('*/26', '*', '*'),
            'Каждые 26 минут',
            )
        self.assertEqual(
            construct_periodic('*/27', '*', '*'),
            'Каждые 27 минут',
            )
        self.assertEqual(
            construct_periodic('*/28', '*', '*'),
            'Каждые 28 минут',
            )
        self.assertEqual(
            construct_periodic('*/29', '*', '*'),
            'Каждые 29 минут',
            )
        self.assertEqual(
            construct_periodic('*/30', '*', '*'),
            'Каждые 30 минут',
            )
        self.assertEqual(
            construct_periodic('*/31', '*', '*'),
            'Каждую 31 минуту',
            )
        self.assertEqual(
            construct_periodic('*/32', '*', '*'),
            'Каждые 32 минуты',
            )
        self.assertEqual(
            construct_periodic('*/33', '*', '*'),
            'Каждые 33 минуты',
            )
        self.assertEqual(
            construct_periodic('*/34', '*', '*'),
            'Каждые 34 минуты',
            )
        self.assertEqual(
            construct_periodic('*/35', '*', '*'),
            'Каждые 35 минут',
            )
        self.assertEqual(
            construct_periodic('*/36', '*', '*'),
            'Каждые 36 минут',
            )
        self.assertEqual(
            construct_periodic('*/37', '*', '*'),
            'Каждые 37 минут',
            )
        self.assertEqual(
            construct_periodic('*/38', '*', '*'),
            'Каждые 38 минут',
            )
        self.assertEqual(
            construct_periodic('*/39', '*', '*'),
            'Каждые 39 минут',
            )
        self.assertEqual(
            construct_periodic('*/40', '*', '*'),
            'Каждые 40 минут',
            )
        self.assertEqual(
            construct_periodic('*/41', '*', '*'),
            'Каждую 41 минуту',
            )
        self.assertEqual(
            construct_periodic('*/42', '*', '*'),
            'Каждые 42 минуты',
            )
        self.assertEqual(
            construct_periodic('*/43', '*', '*'),
            'Каждые 43 минуты',
            )
        self.assertEqual(
            construct_periodic('*/44', '*', '*'),
            'Каждые 44 минуты',
            )
        self.assertEqual(
            construct_periodic('*/45', '*', '*'),
            'Каждые 45 минут',
            )
        self.assertEqual(
            construct_periodic('*/46', '*', '*'),
            'Каждые 46 минут',
            )
        self.assertEqual(
            construct_periodic('*/47', '*', '*'),
            'Каждые 47 минут',
            )
        self.assertEqual(
            construct_periodic('*/48', '*', '*'),
            'Каждые 48 минут',
            )
        self.assertEqual(
            construct_periodic('*/49', '*', '*'),
            'Каждые 49 минут',
            )
        self.assertEqual(
            construct_periodic('*/50', '*', '*'),
            'Каждые 50 минут',
            )
        self.assertEqual(
            construct_periodic('*/51', '*', '*'),
            'Каждую 51 минуту',
            )
        self.assertEqual(
            construct_periodic('*/52', '*', '*'),
            'Каждые 52 минуты',
            )
        self.assertEqual(
            construct_periodic('*/53', '*', '*'),
            'Каждые 53 минуты',
            )
        self.assertEqual(
            construct_periodic('*/54', '*', '*'),
            'Каждые 54 минуты',
            )
        self.assertEqual(
            construct_periodic('*/55', '*', '*'),
            'Каждые 55 минут',
            )
        self.assertEqual(
            construct_periodic('*/56', '*', '*'),
            'Каждые 56 минут',
            )
        self.assertEqual(
            construct_periodic('*/57', '*', '*'),
            'Каждые 57 минут',
            )
        self.assertEqual(
            construct_periodic('*/58', '*', '*'),
            'Каждые 58 минут',
            )
        self.assertEqual(
            construct_periodic('*/59', '*', '*'),
            'Каждые 59 минут',
            )

    def test_construct_time(self):
        """Тест проверки переработки времени
        """
        cron = CrontabSchedule.objects.create(hour=18, minute=30)
        day_now = date.today()
        self.assertEqual(
            construct_time_to_task(
                time_interval=cron,
                ),
            datetime(
                year=day_now.year,
                month=day_now.month,
                day=day_now.day,
                hour=18,
                minute=30,
                tzinfo=timezone.get_current_timezone(),
                ),
            )
