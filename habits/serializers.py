from rest_framework import serializers, status
from rest_framework.response import Response

from habits.models import Habit
from habits.validators import (ValidateInterval,
                               ValidateDateDay,
                               ValidateDateMinute,
                               ValidatorOneValueInput,
                               ValidatorNiceHabit,
                               ValidatorRalatedHabit,
                               ValidatorRelatedHabitSomePublished,
                               )
from habits.handlers import HandleInterval, HandleTimeToDo, HandleTimeToDone


class HabitCreateSearilizer(serializers.ModelSerializer):
    """Сериализатор который отвечает за создание объекта Привычки
    """
    periodic = serializers.CharField(required=True)
    time_to_do = serializers.CharField(required=True)
    time_to_done = serializers.CharField(required=True)
    
    class Meta:
        model = Habit
        fields = ('pk',
                  'place',
                  'time_to_do',
                  'action',
                  'is_nice_habit',
                  'related_habit',
                  'periodic',
                  'reward',
                  'time_to_done',
                  'is_published',
                  )
        validators = (ValidateInterval('periodic'),
                      ValidateDateDay('time_to_do'),
                      ValidateDateMinute('time_to_done'),
                      ValidatorOneValueInput(['related_habit', 'reward']),
                      ValidatorNiceHabit('is_nice_habit', ['is_nice_habit', 'reward', 'related_habit']),
                      ValidatorRalatedHabit('related_habit'),
                      ValidatorRelatedHabitSomePublished('related_habit', ['related_habit', 'is_published']),
                      )
    
    def create(self, validated_data):
        interval = validated_data['periodic']
        time_to_do = validated_data['time_to_do']
        time_to_done = validated_data['time_to_done']
        validated_data['periodic'] = HandleInterval.get_interval(interval)
        validated_data['time_to_do'] = HandleTimeToDo.get_crontab_time(time_to_do)
        validated_data['time_to_done'] = HandleTimeToDone.get_time(time_to_done)
        super().create(validated_data)
        validated_data['periodic'] = f'every {validated_data["periodic"].every} {validated_data["periodic"].period.lower()}'
        validated_data['time_to_do'] = f'{validated_data["time_to_do"].hour}:{validated_data["time_to_do"].minute}'
        return validated_data


class HabitRetieveSearilizer(serializers.ModelSerializer):
    """Сеарилизатор вывода привычки
    """    
    
    
    class Meta:
        model = Habit
        fields = ('pk',
                  'place',
                  'time_to_do',
                  'action',
                  'is_nice_habit',
                  'related_habit',
                  'periodic',
                  'reward',
                  'time_to_done',
                  'is_published',
                  )
