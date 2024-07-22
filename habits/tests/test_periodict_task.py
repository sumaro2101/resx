from rest_framework.test import APITestCase
from rest_framework import status

from django.contrib.auth import get_user_model
from django.urls import reverse

from django_celery_beat.models import PeriodicTask

from habits.models import Habit


class TestPeriodicTask(APITestCase):
    """Тесты преодических задач
    """
    def setUp(self):
        self.user = get_user_model().objects.create_user('owner',
                                                         'owner@gmail.com',
                                                         'ownerpass',
                                                         tg_id=1000000,)
        self.client.force_authenticate(user=self.user)
        url = reverse('habits:habit_create')
        data = {
            'place': 'test_place',
            'time_to_do': '18:41',
            'action': 'test_action',
            'is_nice_habit': False,
            'periodic': '2/0/0',
            'reward': 'test_reward',
            'time_to_done': '1:32',
        }
        self.client.post(url, data, format='json')
        self.habit = Habit.objects.get(place='test_place')
        self.task = PeriodicTask.objects.get(
            name__contains=f'U-{self.user.pk}',
            )

    def test_created_periodic_task(self):
        """Тест созданной периодической задачи
        """
        self.assertTrue(self.task.enabled)
        self.assertEqual(self.habit.time_to_do.hour, '18')
        self.assertEqual(self.task.crontab.day_of_month, '*/2')
        self.assertEqual(self.task.start_time.hour, 12)
        self.assertEqual(self.task.start_time.minute, 41)

    def test_update_periodic_task_two_arguments(self):
        """Тест обновления периодической задачи оба аргумента
        """
        url = reverse('habits:habit_update', kwargs={'pk': self.habit.pk})
        data = {
            'time_to_do': '11:22',
            'periodic': '0/12/0',
        }
        response = self.client.patch(url, data, format='json')
        task = PeriodicTask.objects.get(name__contains=f'U-{self.user.pk}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(task.enabled)
        self.assertEqual(task.crontab.hour, '*/12')
        self.assertEqual(task.start_time.hour, 5)
        self.assertEqual(task.start_time.minute, 22)

    def test_update_periodic_task_period_argument(self):
        """Тест обновления периодической задачи интервал аргумента
        """
        url = reverse('habits:habit_update', kwargs={'pk': self.habit.pk})
        data = {
            'periodic': '0/0/30',
        }
        response = self.client.patch(url, data, format='json')
        task = PeriodicTask.objects.get(name__contains=f'U-{self.user.pk}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(task.enabled)
        self.assertEqual(task.crontab.minute, '*/30')

    def test_update_periodic_no_argument(self):
        """Тест обновления периодической задачи без аргументов времени
        """
        url = reverse('habits:habit_update', kwargs={'pk': self.habit.pk})
        data = {
            'place': 'test_place_update',
            'action': 'test_action_update',
            'reward': 'test_reward_update',
            'time_to_done': '0:11',
        }
        response = self.client.patch(url, data, format='json')
        task = PeriodicTask.objects.get(name__contains=f'U-{self.user.pk}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(task.enabled)
        self.assertEqual(self.task.crontab.day_of_month, '*/2')
        self.assertEqual(self.task.start_time.hour, 12)
        self.assertEqual(self.task.start_time.minute, 41)

    def test_update_periodic_task_time_to_do_argument(self):
        """Тест обновления периодической задачи время выполнения аргумент
        """
        url = reverse('habits:habit_update', kwargs={'pk': self.habit.pk})
        data = {
            'time_to_do': '3:04',
        }
        response = self.client.patch(url, data, format='json')
        task = PeriodicTask.objects.get(name__contains=f'U-{self.user.pk}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(task.enabled)
        self.assertEqual(task.start_time.hour, 21)
        self.assertEqual(task.start_time.minute, 4)

    def test_delete_periodic_task(self):
        """Тест удаления периодической задачи
        """
        url = reverse('habits:habit_delete', kwargs={'pk': self.habit.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.count(), 0)
        self.assertEqual(PeriodicTask.objects.count(), 0)
