from django.contrib.auth.models import AbstractUser
from django.db import models

from phonenumber_field.modelfields import PhoneNumberField
# Create your models here.

class User(AbstractUser):
    """Модель пользователя
    """    
    phone = PhoneNumberField(help_text='Номер телефона, важно указать для интеграции с Telegram. Пример: +7 (900) 910 1000',
                             unique=True,
                             )
    
    tg_id = models.BigIntegerField(verbose_name='ID чата в телеграмме',
                                        null=True,
                                        blank=True,
                                        editable=True,
                                        help_text='ID чата в Telegram,\
                                            нужен для итеграции с Телеграмом и рассылки напоминаний'
                                        )
