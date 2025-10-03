from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Song, Album, Genre, Artist

# Register your models here.
admin.site.register(Song)
admin.site.register(Album)
admin.site.register(Genre)
admin.site.register(Artist)


class CustomUserAdmin(BaseUserAdmin):
    # Add 'favorite_songs' to fieldsets
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Favorites",
            {
                "fields": ("favorite_songs",),
            },
        ),
    )

    # `add_fieldsets` for form to create new User):
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "Favorites",
            {
                "fields": ("favorite_songs",),
            },
        ),
    )

    # Allow to select multiple songs
    filter_horizontal = ("favorite_songs",)


# Unregister default User
admin.site.unregister(User)

# Register again with custom admin
admin.site.register(User, CustomUserAdmin)
