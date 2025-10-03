from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    # Index
    path("", views.index, name="index"),
    # User
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("user/logout/", views.logout_view, name="logout"),
    path("user/", views.profile, name="profile"),
    path("user/favorite/", views.favorite_songs, name="favorite"),
    # Song
    path("songs/", views.songs, name="songs"),
    path("song/<int:song_id>/detail/", views.song_detail, name="song_detail"),
    path(
        "song/<int:song_id>/favorite/", views.song_to_favorite, name="song_to_favorite"
    ),
    path("song/<int:song_id>/song-albums/", views.song_to_album, name="song_to_album"),
    # Album
    path("user/albums/", views.albums, name="albums"),
    path("user/album/<int:album_id>/detail/", views.album_detail, name="album_detail"),
    path("user/album/create/", views.album_create, name="album_create"),
    path("user/album/<int:album_id>/delete/", views.album_delete, name="album_delete"),
    path(
        "user/album/<int:album_id>/song/<int:song_id>/remove",
        views.album_remove_song,
        name="album_remove_song",
    ),
    # Artists
    path("artists/", views.artists, name="artists"),
    path("artist/<int:artist_id>/detail/", views.artist_detail, name="artist_detail"),
    # Search
    path("search/", views.search, name="search"),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
