from django.urls import path

from habits.apps import HabitsConfig
from habits.views import (HabitCreateAPIView,
                          )

app_name = HabitsConfig.name

urlpatterns = [
    path('api/habit/create/', HabitCreateAPIView.as_view(), name='habit_create')
]
