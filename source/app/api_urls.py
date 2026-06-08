from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

from . import api_views

urlpatterns = [
    # Home
    path("", api_views.IndexAPIView.as_view(), name="api-home"),

    # Authentication
    path("auth/register/", api_views.RegisterAPIView.as_view(), name="api-register"),
    path("auth/login/", api_views.LoginAPIView.as_view(), name="api-login"),
    path("auth/logout/", api_views.LogoutAPIView.as_view(), name="api-logout"),
    path("auth/profile/", api_views.ProfileAPIView.as_view(), name="api-profile"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="api-token-refresh"),
    path("auth/verify/", TokenVerifyView.as_view(), name="api-token-verify"),

    # Songs
    path("songs/", api_views.SongListAPIView.as_view(), name="api-song-list"),
    path("songs/<int:pk>/", api_views.SongDetailAPIView.as_view(), name="api-song-detail"),

    # Favorites
    path(
        "favorites/",
        api_views.FavoriteSongListAPIView.as_view(),
        name="api-favorite-list",
    ),
    path(
        "songs/<int:song_id>/favorite/",
        api_views.toggle_favorite,
        name="api-song-favorite",
    ),

    # Artists
    path("artists/", api_views.ArtistListAPIView.as_view(), name="api-artist-list"),
    path(
        "artists/<int:pk>/",
        api_views.ArtistDetailAPIView.as_view(),
        name="api-artist-detail",
    ),

    # Albums
    path("albums/", api_views.AlbumListAPIView.as_view(), name="api-album-list"),
    path(
        "albums/<int:pk>/",
        api_views.AlbumDetailAPIView.as_view(),
        name="api-album-detail",
    ),
    path(
        "albums/<int:album_id>/songs/<int:song_id>/",
        api_views.album_add_song,
        name="api-album-song-add",
    ),
    path(
        "albums/<int:album_id>/songs/<int:song_id>/remove/",
        api_views.album_remove_song,
        name="api-album-song-remove",
    ),

    # Genres
    path("genres/", api_views.GenreListAPIView.as_view(), name="api-genre-list"),
    path(
        "genres/<int:pk>/",
        api_views.GenreDetailAPIView.as_view(),
        name="api-genre-detail",
    ),

    # Search
    path("search/", api_views.search, name="api-search"),
]
