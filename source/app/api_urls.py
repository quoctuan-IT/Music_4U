from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

from . import api_views

urlpatterns = [
    # Index
    path("", api_views.IndexAPIView.as_view(), name="api-index"),
    # JWT Auth
    path("auth/register/", api_views.RegisterAPIView.as_view(), name="api-register"),
    path("auth/login/", api_views.LoginAPIView.as_view(), name="api-login"),
    path("auth/logout/", api_views.LogoutAPIView.as_view(), name="api-logout"),
    path("auth/profile/", api_views.ProfileAPIView.as_view(), name="api-profile"),
    # Token
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # Songs
    path("songs/", api_views.SongListAPIView.as_view(), name="api-song-list"),
    path(
        "songs/<int:pk>/", api_views.SongDetailAPIView.as_view(), name="api-song-detail"
    ),
    path(
        "songs/<int:song_id>/favorite/",
        api_views.toggle_favorite,
        name="api-toggle-favorite",
    ),
    path(
        "songs/favorites/",
        api_views.FavoriteSongListAPIView.as_view(),
        name="api-favorite-songs",
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
        "albums/<int:album_id>/songs/<int:song_id>/add/",
        api_views.album_add_song,
        name="api-album-add-song",
    ),
    path(
        "albums/<int:album_id>/songs/<int:song_id>/remove/",
        api_views.album_remove_song,
        name="api-album-remove-song",
    ),
    # Genres
    path("genres/", api_views.GenreListAPIView.as_view(), name="api-genre-list"),
    path(
        "genres/<int:pk>/",
        api_views.GenreDetailAPIView.as_view(),
        name="api-genre-detail",
    ),
    # Search
    path("search/", api_views.search_songs, name="api-search"),
    # Admin CRUD
    path(
        "admin/songs/",
        api_views.AdminSongListCreateAPIView.as_view(),
        name="api-admin-songs",
    ),
    path(
        "admin/songs/<int:pk>/",
        api_views.AdminSongDetailAPIView.as_view(),
        name="api-admin-song-detail",
    ),
    path(
        "admin/artists/",
        api_views.AdminArtistListCreateAPIView.as_view(),
        name="api-admin-artists",
    ),
    path(
        "admin/artists/<int:pk>/",
        api_views.AdminArtistDetailAPIView.as_view(),
        name="api-admin-artist-detail",
    ),
    path(
        "admin/genres/",
        api_views.AdminGenreListCreateAPIView.as_view(),
        name="api-admin-genres",
    ),
    path(
        "admin/genres/<int:pk>/",
        api_views.AdminGenreDetailAPIView.as_view(),
        name="api-admin-genre-detail",
    ),
]
