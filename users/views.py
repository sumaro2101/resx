from rest_framework import generics

from django.contrib.auth import get_user_model

from users.serializers import (UserProfileSerializer,
                               UserProfileCreateSerializer
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
    