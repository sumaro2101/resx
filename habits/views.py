from rest_framework import generics, status
from rest_framework.response import Response

from habits.models import Habit
from habits.serializers import (HabitCreateSearilizer,
                                HabitRetieveSearilizer,
                                )


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
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not request.user == instance.owner:
            response = {
                'published': 'Данную привычку может просматривать только владелец'
            }
            return Response(data=response, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    
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
        return queryset.filter(owner=self.request.user)
    