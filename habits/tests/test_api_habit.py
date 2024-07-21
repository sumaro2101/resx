from datetime import timedelta

from rest_framework.test import APITestCase
from rest_framework import status

from django.contrib.auth import get_user_model
from django.urls import reverse

from django_celery_beat.models import CrontabSchedule, PeriodicTask

from habits.models import Habit


class TestAPIHabit(APITestCase):
    """Тесты API привычек
    """
    
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user('user',
                                                         'user@gmail.com',
                                                         'usertestuser',
                                                         )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('habits:habit_create')
        self.cron = CrontabSchedule.objects.create(hour=18, minute=41)
        self.interval = CrontabSchedule.objects.create(minute=0, hour=0, day_of_month='*/1')
        
    def test_create_habit(self):
        """Тест создания привычки
        """
        data = {
            'place': 'test_place',
            'time_to_do': '18:41',
            'action': 'test_action',
            'is_nice_habit': False,
            'periodic': '2/0/0',
            'reward': 'test_reward',
            'time_to_done': '1:32',
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {"place": "test_place",
                                        "time_to_do": "18:41",
                                        "action": "test_action",
                                        "is_nice_habit": False,
                                        "related_habit": None,
                                        "periodic": "*/2/*/*",
                                        "reward": "test_reward",
                                        "time_to_done": "0:01:32",
                                        })
        self.assertEqual(PeriodicTask.objects.count(), 1)

    def test_create_habit_bad_request_input_two_values(self):
        """Тест проверки вхождения двух полей которые не могут быть вместе
        """
        habit = Habit.objects.create(owner=self.user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=True,
                                     periodic=self.interval,
                                     reward=None,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     )
        data = {
            'place': 'test_place',
            'time_to_do': '18:41',
            'action': 'test_action',
            'is_nice_habit': False,
            'related_habit': habit.pk,
            'periodic': '2/0/0',
            'reward': 'test_reward',
            'time_to_done': '1:32',
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['error'][0]), 'related_habit и reward не могут быть определенны вместе')
        self.assertEqual(PeriodicTask.objects.count(), 0)
        
    def test_create_habit_bad_request_related_habbit_is_not_nice(self):
        """Тест проверки вхождения связанной модели с полезной привычкой
        """
        habit = Habit.objects.create(owner=self.user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=False,
                                     periodic=self.interval,
                                     reward='reward',
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     )
        data = {
            'place': 'test_place',
            'time_to_do': '18:41',
            'action': 'test_action',
            'is_nice_habit': False,
            'related_habit': habit.pk,
            'periodic': '2/0/0',
            'reward': None,
            'time_to_done': '1:32',
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['related_habit'][0]), 'Связаная привычка может быть только приятной')
        
    def test_create_habit_bad_request_nice_habit(self):
        """Тест проверки приятной привычки с неправильными аргументами
        """        
        data = {
            'place': 'test_place',
            'time_to_do': '18:41',
            'action': 'test_action',
            'is_nice_habit': True,
            'periodic': '2/0/0',
            'reward': 'reward',
            'time_to_done': '1:32',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['is_nice_habit'][0]), 'При указании приятной привычки награду и связаную привычку указывать нельзя')
        self.assertEqual(PeriodicTask.objects.count(), 0)

    def test_create_habit_bad_request_related_habbit_is_some_publish(self):
        """Тест проверки вхождения связанной модели не с одинаковой публичностью
        """
        habit = Habit.objects.create(owner=self.user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=True,
                                     periodic=self.interval,
                                     reward=None,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=False,
                                     )
        data = {
            'place': 'test_place',
            'time_to_do': '18:41',
            'action': 'test_action',
            'is_nice_habit': False,
            'related_habit': habit.pk,
            'periodic': '2/0/0',
            'reward': None,
            'time_to_done': '1:32',
            'is_published': True,
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['related_habit'][0]), 'Связанная привычка и текущая не могут иметь разные статусы публичности')
        
    def test_create_habit_with_related_habit(self):
        """Тест проверки вхождения связанной модели с одинаковой публичностью
        """
        habit = Habit.objects.create(owner=self.user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=True,
                                     periodic=self.interval,
                                     reward=None,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=False,
                                     )
        data = {
            'place': 'test_place',
            'time_to_do': '18:41',
            'action': 'test_action',
            'is_nice_habit': False,
            'related_habit': habit.pk,
            'periodic': '2/0/0',
            'reward': None,
            'time_to_done': '1:32',
            'is_published': False,
        }
        response = self.client.post(self.url, data, format='json')
        count_in_bd = Habit.objects.count()
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(count_in_bd, 2)
    
    def test_retrieve_habit_private(self):
        """Тест отказа в просмотре приватной привычки
        """
        user = get_user_model().objects.create_user('owner', 'owner@gmail.com', 'ownerpass', phone='+7(900)9001000')
        habit = Habit.objects.create(owner=user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=True,
                                     periodic=self.interval,
                                     reward=None,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=False,
                                     )
        url = reverse('habits:habit_retrieve', kwargs={'pk': habit.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_habit_bad_related_habit(self):
        """Тест привязки чужой привычки
        """
        user = get_user_model().objects.create_user('owner', 'owner@gmail.com', 'ownerpass', phone='+7(900)9001000')    
        related = Habit.objects.create(owner=user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=True,
                                     periodic=self.interval,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=True,
                                     )
        data = {
            'place': 'test_place',
            'time_to_do': '18:41',
            'action': 'test_action',
            'is_nice_habit': False,
            'related_habit': related.pk,
            'periodic': '2/0/0',
            'time_to_done': '1:32',
            'is_published': True,
        }
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_list_of_habits_personal(self):
        """Тест списка привычек связанных с пользователем
        """        
        url = reverse('habits:habit_list_private')
        user = get_user_model().objects.create_user('owner', 'owner@gmail.com', 'ownerpass', phone='+7(900)9001000')    
        Habit.objects.create(owner=user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=True,
                                     periodic=self.interval,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=True,
                                     )
        
        Habit.objects.create(owner=self.user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=True,
                                     periodic=self.interval,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=True,
                                     )
        
        responce = self.client.get(url)
        self.assertEqual(responce.status_code, status.HTTP_200_OK)
        self.assertEqual(responce.data['count'], 1)
        
    def test_habit_retrieve_block_view(self):
        """Тест блокировки доступа к привычке не являющейся личной
        """
        user = get_user_model().objects.create_user('owner', 'owner@gmail.com', 'ownerpass', phone='+7(900)9001000')    
        habit = Habit.objects.create(owner=user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=True,
                                     periodic=self.interval,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=True,
                                     )
        url = reverse('habits:habit_retrieve', kwargs={'pk': habit.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(str(response.data), "{'detail': ErrorDetail(string='You do not have permission to perform this action.', code='permission_denied')}")
        
    def test_list_of_habits_published(self):
        """Тест списка привычек связанных с пользователем
        """        
        url = reverse('habits:habit_list')
        user = get_user_model().objects.create_user('owner', 'owner@gmail.com', 'ownerpass', phone='+7(900)9001000')
        Habit.objects.create(owner=user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=True,
                                     periodic=self.interval,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=True,
                                     )
        
        Habit.objects.create(owner=self.user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=True,
                                     periodic=self.interval,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=True,
                                     )
        
        responce = self.client.get(url)
        self.assertEqual(responce.status_code, status.HTTP_200_OK)
        self.assertEqual(responce.data['count'], 2)
        
    def test_habit_update(self):
        """Тест обновления привычки
        """
        habit = Habit.objects.create(owner=self.user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=False,
                                     periodic=self.interval,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=True,
                                     )
        url = reverse('habits:habit_update', kwargs={'pk': habit.pk})
        data = {
            'place': 'update_place',
            'time_to_do': '20:30',
            'action': 'update_action',
            'periodic': '4/0/0',
            'reward': 'update_reward',
            'time_to_done': '0:59',
            'is_published': False,
        }
        responce = self.client.patch(url, data)
        self.assertEqual(responce.status_code, status.HTTP_200_OK)
        self.assertEqual(responce.data['place'], 'update_place')
        self.assertEqual(responce.data['time_to_done'], '0:00:59')
    
    def test_habit_update_change_raleted_published(self):
        """Тест изменения публичности у связанной привычки при изменении у основной
        """        
        ralated = Habit.objects.create(owner=self.user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=True,
                                     periodic=self.interval,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=True,
                                     )
        
        habit = Habit.objects.create(owner=self.user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=False,
                                     related_habit=ralated,
                                     periodic=self.interval,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=True,
                                     )
        
        data_habit = {
            'is_published': False
        }
        
        url_habit = reverse('habits:habit_update', kwargs={'pk': habit.pk})
        
        responce_habit = self.client.patch(url_habit, data_habit)
        
        habit = Habit.objects.get(pk=habit.pk)
        ralated = Habit.objects.get(pk=ralated.pk)
        self.assertEqual(responce_habit.status_code, status.HTTP_200_OK)
        self.assertEqual(habit.is_published, False)
        self.assertEqual(ralated.is_published, False)
        
        data_ralated = {
            'is_published': True
        }
        
        url_ralated = reverse('habits:habit_update', kwargs={'pk': ralated.pk})
        
        responce_ralated = self.client.patch(url_ralated, data_ralated)
        habit = Habit.objects.get(pk=habit.pk)
        ralated = Habit.objects.get(pk=ralated.pk)
        self.assertEqual(responce_ralated.status_code, status.HTTP_200_OK)
        self.assertEqual(ralated.is_published, True)
        self.assertEqual(habit.is_published, True)
        
    def test_habit_update_block_permission(self):
        """Тест блокировки доступа к изменению привычки если не является владельцем
        """
        user = get_user_model().objects.create_user('owner', 'owner@gmail.com', 'ownerpass', phone='+7(900)9001000')
        habit = Habit.objects.create(owner=user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=False,
                                     periodic=self.interval,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=True,
                                     )
        url = reverse('habits:habit_update', kwargs={'pk': habit.pk})
        data = {
            'place': 'update_place',
            'time_to_do': '20:30',
            'action': 'update_action',
            'periodic': '4/0/0',
            'reward': 'update_reward',
            'time_to_done': '0:59',
            'is_published': False,
        }
        responce = self.client.patch(url, data)
        
        self.assertEqual(responce.status_code, status.HTTP_403_FORBIDDEN)

    def test_habit_delete(self):
        """Тест удаления привычки
        """
        habit = Habit.objects.create(owner=self.user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=False,
                                     periodic=self.interval,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=True,
                                     )
        url = reverse('habits:habit_delete', kwargs={'pk': habit.pk})
        responce = self.client.delete(url)
        
        self.assertEqual(responce.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.count(), 0)

    def test_habit_delete_save_related(self):
        """Тест удаления основной и сохранение связанной
        """
        related = Habit.objects.create(owner=self.user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=True,
                                     periodic=self.interval,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=True,
                                     )
        
        habit = Habit.objects.create(owner=self.user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=False,
                                     related_habit=related,
                                     periodic=self.interval,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=True,
                                     )
        url = reverse('habits:habit_delete', kwargs={'pk': related.pk})
        responce = self.client.delete(url)
        habit = Habit.objects.get(pk=habit.pk)
        
        self.assertEqual(responce.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.count(), 1)
        self.assertEqual(habit.related_habit, None)
        
    def test_habit_delete_block_permission(self):
        """Тест блокировки доступа к удалению привычки если не является владельцем
        """
        user = get_user_model().objects.create_user('owner', 'owner@gmail.com', 'ownerpass', phone='+7(900)9001000')
        habit = Habit.objects.create(owner=user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=False,
                                     periodic=self.interval,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=True,
                                     )
        url = reverse('habits:habit_delete', kwargs={'pk': habit.pk})
        responce = self.client.delete(url)
        
        self.assertEqual(responce.status_code, status.HTTP_403_FORBIDDEN)
        