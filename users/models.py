from django.db import models
from django.contrib.auth.models import AbstractUser

from phonenumber_field.modelfields import PhoneNumberField
# Create your models here.

class User(AbstractUser):
    """Модель пользователя
    """    
    phone = PhoneNumberField(help_text='Номер телефона, важно указать для интеграции с Telegram')
