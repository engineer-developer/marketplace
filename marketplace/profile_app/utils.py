from django.contrib.auth.models import User
from django.db.models.fields.files import ImageFieldFile
from rest_framework.response import Response

from mainsite.handle_errors import handle_serializer_not_valid
from mainsite.main_logger import logger
from profile_app.models import Profile
from profile_app.serializers import ProfileUpdateSerializer


def create_user_profile(user: User) -> None:
    """Создание профиля пользователя"""

    profile = Profile.objects.create(user=user)

    if user.first_name or user.last_name:
        profile.fullName = user.get_full_name()
    else:
        profile.fullName = user.username

    profile.save()
    logger.debug("Profile for user '%s' is created", profile.user)


def update_user_profile(profile: Profile, data: dict) -> Profile | Response:
    """Обновляет профиль пользователя переданными данными"""

    serializer = ProfileUpdateSerializer(profile, data=data)
    if not serializer.is_valid():
        return handle_serializer_not_valid(serializer)

    updated_profile = serializer.save()
    logger.debug("Profile for user '%s' is updated", updated_profile.user)
    return updated_profile


def update_user_data_with_profile(user: User) -> None:
    """Обновляет данные пользователя данными из его профиля"""

    profile = user.profile

    if profile.fullName and profile.fullName.find(" ") > -1:
        user.first_name, user.last_name = profile.fullName.split(
            sep=" ",
            maxsplit=1,
        )

    if profile.email:
        user.email = profile.email

    user.save()
    logger.debug("User '%s' info updated from %s", user, profile)
