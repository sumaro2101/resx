from rest_framework import generics

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser

from users.serializers import (UserProfileSerializer,
                               UserProfileCreateSerializer,
                               UserProfileUpdateSerializer,
                               )

class UserProfileViewAPI(generics.RetrieveAPIView):
    """Профиль пользователя
    """    
    queryset = get_user_model().objects.filter(is_active=True)
    serializer_class = UserProfileSerializer


class UserCreateProfileAPI(generics.CreateAPIView):
    """Создание нового пользователя
    """
    queryset = get_user_model().objects.get_queryset()
    serializer_class = UserProfileCreateSerializer
    
    
class UserUpdateProfileAPI(generics.UpdateAPIView):
    """Редактировае пользователя
    """
    queryset = get_user_model().objects.get_queryset()
    serializer_class = UserProfileUpdateSerializer
    

class UserDeleteProfuleAPI(generics.DestroyAPIView):
    """Изменения активности пользователя
    """    
    queryset = get_user_model().objects.get_queryset()
    
    def perform_destroy(self, instance: AbstractUser) -> None:
        instance.is_active = False
        instance.save(update_fields=('is_active',))
