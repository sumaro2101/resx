from rest_framework import serializers

from django.db import transaction

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
    
    def _handle_times(self, validated_data: dict) -> dict:
        """Точка входа в обработчик всех дат привычки
        """        
        validated_data = validated_data
        if interval := validated_data.get('periodic'):
            validated_data['periodic'] = HandleInterval.get_interval(interval)
            
        if time_to_do := validated_data.get('time_to_do'):
            validated_data['time_to_do'] = HandleTimeToDo.get_crontab_time(time_to_do)
            
        if time_to_done := validated_data.get('time_to_done'):
            validated_data['time_to_done'] = HandleTimeToDone.get_time(time_to_done)
        return validated_data
    
    def create(self, validated_data):
        validated_data = self._handle_times(validated_data)
        super().create(validated_data)
        validated_data['periodic'] = f'every {validated_data["periodic"].every} {validated_data["periodic"].period.lower()}'
        validated_data['time_to_do'] = f'{validated_data["time_to_do"].hour}:{validated_data["time_to_do"].minute}'
        return validated_data
    
    def update(self, instance, validated_data):
        is_published_changed = validated_data['is_published']
        validated_data = self._handle_times(validated_data)
        with transaction.atomic():
            instance = super().update(instance, validated_data)
            if is_published_changed is not None:
                related_habit = instance.related_habit
                if related_habit:
                    related_habit.is_published = is_published_changed
                    related_habit.save(update_fields=('is_published',))
                    ralated_habit = Habit.objects.filter(related_habit=related_habit)
                    ralated_habit.update(is_published=is_published_changed)
                else:
                    try:
                        ralated_habit = Habit.objects.filter(related_habit=instance)
                        ralated_habit.update(is_published=is_published_changed)
                        ralated_habit.related_habit.update(is_published=is_published_changed)
                    except:
                        pass
        return instance
        

class HabitRelatedRetieveSearilizer(serializers.ModelSerializer):
    """Сеарилизатор вывода связанной привычки
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


class HabitRetieveSearilizer(serializers.ModelSerializer):
    """Сеарилизатор вывода привычки
    """
    related_habit = HabitRelatedRetieveSearilizer(source='related', many=True)
    
    
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
    