from rest_framework import generics, status
from rest_framework.response import Response

from django.db.models import Q

from habits.models import Habit
from habits.serializers import (HabitCreateSearilizer,
                                HabitRetieveSearilizer,
                                )
from habits.permissions import IsCurrentUser


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
    queryset = Habit.objects.get_queryset()
    serializer_class = HabitRetieveSearilizer
    permission_classes = [IsCurrentUser]


class HabitListAPIView(generics.ListAPIView):
    """Список публичных привычек
    """
    queryset = Habit.objects.filter(is_published=True)
    serializer_class = HabitRetieveSearilizer
    
    
class HabitUserListAPIView(generics.ListAPIView):
    """Список личных привычек
    """
    queryset = Habit.objects.get_queryset()
    serializer_class = HabitRetieveSearilizer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(Q(owner=self.request.user))
    