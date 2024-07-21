from rest_framework import generics, status
from rest_framework.response import Response

from django.db.models import Q
from django_celery_beat.models import PeriodicTask

from habits.models import Habit
from habits.serializers import (HabitCreateSearilizer,
                                HabitRetieveSearilizer,
                                )
from habits.permissions import IsCurrentUser, IsAdmin
from habits.paginators import PaginateHabits


class HabitCreateAPIView(generics.CreateAPIView):
    """Создание привычки
    """
    queryset = Habit.objects.get_queryset()
    serializer_class = HabitCreateSearilizer
    
    def create(self, request, *args, **kwargs):
        owner_related_habit = request.data.get('related_habit')
        if owner_related_habit:
            if self.request.user != self.queryset.get(pk=request.data['related_habit']).owner:
                return Response(data={'related_habit': 'Связаная привычка может быть только ваша'}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class HabitRetieveAPIView(generics.RetrieveAPIView):
    """Показание привычки
    """
    queryset = Habit.objects.get_queryset().select_related('owner', 'time_to_do', 'related_habit', 'periodic',)
    serializer_class = HabitRetieveSearilizer
    permission_classes = [IsCurrentUser | IsAdmin]


class HabitListAPIView(generics.ListAPIView):
    """Список публичных привычек
    """
    queryset = Habit.objects.filter(Q(is_published=True)).select_related('owner', 'time_to_do', 'related_habit', 'periodic',)
    serializer_class = HabitRetieveSearilizer
    pagination_class = PaginateHabits
    
    
class HabitUserListAPIView(generics.ListAPIView):
    """Список личных привычек
    """
    queryset = Habit.objects.get_queryset().select_related('owner', 'time_to_do', 'related_habit', 'periodic',)
    serializer_class = HabitRetieveSearilizer
    pagination_class = PaginateHabits
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            return queryset.filter(Q(owner=self.request.user))
        return queryset
    

class HabitUpdateAPIView(generics.UpdateAPIView):
    """Обновление привычки
    """    
    queryset = Habit.objects.get_queryset().select_related('owner', 'time_to_do', 'related_habit', 'periodic',)
    serializer_class = HabitCreateSearilizer
    permission_classes = [IsCurrentUser | IsAdmin]
    

class HabitDeleteAPIView(generics.DestroyAPIView):
    """Удаление привычки
    """ 
    queryset = Habit.objects.get_queryset()
    permission_classes = [IsCurrentUser | IsAdmin]
    
    def perform_destroy(self, instance):
        PeriodicTask.objects.filter(name__contains=f'_{instance.pk}').delete()
        return super().perform_destroy(instance)
    