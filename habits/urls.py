from django.urls import path

from habits.apps import HabitsConfig
from habits.views import (HabitCreateAPIView,
                          HabitRetieveAPIView,
                          HabitListAPIView,
                          HabitUserListAPIView,
                          )

app_name = HabitsConfig.name

urlpatterns = [
    path('api/habit/create/', HabitCreateAPIView.as_view(), name='habit_create'),
    path('api/habit/list/', HabitListAPIView.as_view(), name='habit_list'),
    path('api/habit/list/private/', HabitUserListAPIView.as_view(), name='habit_list_private'),
    path('api/habit/retrieve/<int:pk>/', HabitRetieveAPIView.as_view(), name='habit_retrieve'),
]
