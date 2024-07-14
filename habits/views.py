from rest_framework import generics

from habits.models import Habit
from habits.serializers import HabitCreateSearilizer

class HabitCreateAPIView(generics.CreateAPIView):
    """Создание привычки
    """
    queryset = Habit.objects.get_queryset()
    serializer_class = HabitCreateSearilizer
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
