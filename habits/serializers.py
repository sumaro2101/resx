from rest_framework import serializers

from habits.models import Habit
from habits.validators import ValidateInterval, ValidateDateDay, ValidateDateMinute
from habits.handlers import HandleInterval, HandleTimeToDo, HandleTimeToDone


class HabitCreateSearilizer(serializers.ModelSerializer):
    """Сериализатор который отвечает за создание объекта Привычки
    """
    periodic = serializers.CharField(required=True)
    time_to_do = serializers.CharField(required=True)
    time_to_done = serializers.CharField(required=True)
    
    class Meta:
        model = Habit
        fields = ('place',
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
                      )
    
    def create(self, validated_data):
        interval = validated_data['periodic']
        time_to_do = validated_data['time_to_do']
        time_to_done = validated_data['time_to_done']
        validated_data['periodic'] = HandleInterval.get_interval(interval)
        validated_data['time_to_do'] = HandleTimeToDo.get_crontab_time(time_to_do)
        validated_data['time_to_done'] = HandleTimeToDone.get_time(time_to_done)
        return super().create(validated_data)
    