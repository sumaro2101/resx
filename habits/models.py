from datetime import timedelta

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from django_celery_beat.models import CrontabSchedule


class Habit(models.Model):
    """Модель привычек пользователя
    """    
    owner = models.ForeignKey(get_user_model(),
                              verbose_name=('создатель привычки'),
                              help_text='Создатель привычки',
                              on_delete=models.CASCADE,
                              )
    
    place = models.CharField(max_length=200,
                             verbose_name='место выполнения привычки',
                             help_text='Место обозначающее выполнение привычки',
                             )
    
    time_to_do = models.ForeignKey(CrontabSchedule,
                                   verbose_name='время выполнения привычки',
                                   on_delete=models.CASCADE,
                                   help_text='Установленное время в которое будет выполнена привычка',
                                   )
    
    action = models.TextField(verbose_name='действие',
                              help_text='Выполняемое действие привычки',
                              )
    
    is_nice_habit = models.BooleanField(verbose_name='признак приятной привычки',
                                        help_text='Поле обозначающее приятная ли эта привычка',
                                        )
    
    related_habit = models.ForeignKey("self",
                                      verbose_name='связанная привычка',
                                      on_delete=models.SET_NULL,
                                      related_name='related',
                                      help_text='Связанная привычка, создает некую цепочку из привычек.\
                                          Последняя привычка может быть "Приятной",\
                                              в этом случае она может быть только последней',
                                      blank=True,
                                      null=True,
                                      )
    
    periodic = models.DurationField(verbose_name='периодичность',
                                    help_text='Установленная периодичность для выполнения,\
                                        устанавливается так же для отправки напоминаний',
                                    default=timedelta(days=1),
                                    )
    
    reward = models.TextField(verbose_name='возраграждение',
                              help_text='Возраграждение за выполнение привычки',
                              blank=True,
                              null=True,
                              )
    
    time_to_done = models.DurationField(verbose_name='время выполнения',
                                        help_text='Неоходимое время для выполнения привычки, не должно быть более чем\
                                            120 сек. или 2 минуты',
                                        )
    
    is_published = models.BooleanField(default=False,
                                       verbose_name='публичность',
                                       help_text='Значение публичности, значение True дает возможность видеть эту привычку другим пользователям',
                                       )
    
    class Meta:
        verbose_name = _("Habit")
        verbose_name_plural = _("Habits")

    def __str__(self):
        return f'{self.action}: {self.time_to_do}'

    def get_absolute_url(self):
        return reverse("habits:habit_detail", kwargs={"pk": self.pk})
