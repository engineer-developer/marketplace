from django.contrib import admin
from django.db.models.fields.files import ImageFieldFile

from profile_app.models import Profile, Avatar


class AvatarInline(admin.TabularInline):
    """Inline для модели аватара"""

    model = Avatar


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Админка профиля пользователя"""

    list_display = (
        "id",
        "user",
        "fullName",
        "email",
        "phone",
        "avatar_file",
    )
    list_display_links = ("user",)
    fields = ("fullName", "email", "phone")
    ordering = ("user",)
    inlines = (AvatarInline,)

    def avatar_file(self, obj: Profile) -> str:
        """Получение имени файла аватара"""

        image: ImageFieldFile = obj.avatar.src
        image_path: str = image.path
        file_name: str = image_path.split("/")[-1]
        return file_name

    def get_queryset(self, request):
        user = request.user
        qs = super().get_queryset(request)
        if user.groups.filter(name__in=["admins", "seller_assistants"]):
            return qs
        return qs.filter(user=request.user)


@admin.register(Avatar)
class AvatarAdmin(admin.ModelAdmin):
    """Админка аватара"""

    list_display = (
        "id",
        "user",
        "src",
        "alt",
    )
    list_display_links = ("user", "src")
    fields = ("src", "alt")

    def user(self, obj: Avatar) -> str:
        """Получение поля user"""
        return obj.profile.user.username

    def get_queryset(self, request):
        user = request.user
        qs = super().get_queryset(request)
        if user.groups.filter(name__in=["admins", "seller_assistants"]):
            return qs
        return qs.filter(profile__user=request.user)
