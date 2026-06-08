from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Song, Artist, Genre, Album
from .serializers import (
    SongSerializer,
    ArtistSerializer,
    GenreSerializer,
    AlbumSerializer,
    UserSerializer,
    RegisterSerializer,
)

HOME_LIMIT = 5


def _home_limit(queryset, request):
    limit = request.query_params.get("limit")
    if limit is None:
        return queryset[:HOME_LIMIT]
    try:
        n = int(limit)
    except (TypeError, ValueError):
        return queryset[:HOME_LIMIT]
    if n <= 0:
        return queryset
    return queryset[:n]


# ---------------------------------------------------------------------------
# Home
# ---------------------------------------------------------------------------


class IndexAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        songs = _home_limit(Song.objects.all().order_by("-id"), request)
        artists = _home_limit(Artist.objects.all().order_by("-id"), request)
        return Response(
            {
                "songs": SongSerializer(songs, many=True, context={"request": request}).data,
                "artists": ArtistSerializer(artists, many=True, context={"request": request}).data,
            }
        )


# ---------------------------------------------------------------------------
# Auth (register, login, logout, profile, favorites)
# ---------------------------------------------------------------------------


class LoginAPIView(TokenObtainPairView):
    pass


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user_id": user.id,
                "message": "Register successfully!",
            },
            status=status.HTTP_201_CREATED,
        )


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Logged out successfully!"},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
class ProfileAPIView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)


# ---------------------------------------------------------------------------
# Favorites
# ---------------------------------------------------------------------------


@permission_classes([IsAuthenticated])
class FavoriteSongListAPIView(generics.ListAPIView):
    serializer_class = SongSerializer

    def get_queryset(self):
        return self.request.user.favorite_songs.all()


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_favorite(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    user = request.user

    if song in user.favorite_songs.all():
        user.favorite_songs.remove(song)
        is_favorite = False
    else:
        user.favorite_songs.add(song)
        is_favorite = True

    return Response({"is_favorite": is_favorite})


# ---------------------------------------------------------------------------
# Songs
# ---------------------------------------------------------------------------


class SongListAPIView(generics.ListAPIView):
    serializer_class = SongSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Song.objects.all().order_by("-id")

    def list(self, request, *args, **kwargs):
        queryset = _home_limit(self.get_queryset(), request)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SongDetailAPIView(generics.RetrieveAPIView):
    queryset = Song.objects.all()
    serializer_class = SongSerializer
    permission_classes = [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        song = self.get_object()
        data = self.get_serializer(song).data
        data["is_favorite"] = False
        data["user_albums"] = []

        if request.user.is_authenticated:
            data["is_favorite"] = song in request.user.favorite_songs.all()
            data["user_albums"] = AlbumSerializer(
                Album.objects.filter(user=request.user), many=True
            ).data

        return Response(data)


# ---------------------------------------------------------------------------
# Artists
# ---------------------------------------------------------------------------


class ArtistListAPIView(generics.ListAPIView):
    serializer_class = ArtistSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Artist.objects.all().order_by("-id")

    def list(self, request, *args, **kwargs):
        queryset = _home_limit(self.get_queryset(), request)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ArtistDetailAPIView(generics.RetrieveAPIView):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    permission_classes = [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        artist = self.get_object()
        songs = Song.objects.filter(artist=artist).order_by("-id")
        return Response(
            {
                **ArtistSerializer(artist, context={"request": request}).data,
                "songs": SongSerializer(songs, many=True, context={"request": request}).data,
            }
        )


# ---------------------------------------------------------------------------
# Genres
# ---------------------------------------------------------------------------


class GenreListAPIView(generics.ListAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [AllowAny]


class GenreDetailAPIView(generics.RetrieveAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [AllowAny]


# ---------------------------------------------------------------------------
# Albums
# ---------------------------------------------------------------------------


class AlbumListAPIView(generics.ListCreateAPIView):
    serializer_class = AlbumSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Album.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AlbumDetailAPIView(generics.RetrieveDestroyAPIView):
    serializer_class = AlbumSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Album.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        album = self.get_object()
        name = album.name
        self.perform_destroy(album)
        return Response(
            {"message": f"Album '{name}' deleted."},
            status=status.HTTP_200_OK,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def album_add_song(request, album_id, song_id):
    song = get_object_or_404(Song, id=song_id)
    album = get_object_or_404(Album, id=album_id, user=request.user)

    if not album:
        return Response(
            {"error": "Album not found"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if song in album.songs.all():
        return Response(
            {
                "message": f"'{song.title}' is already in the album '{album.name}'.",
                "already_in_album": True,
            },
            status=status.HTTP_200_OK,
        )

    album.songs.add(song)
    return Response(
        {
            "message": f"'{song.title}' was added to album '{album.name}'.",
            "already_in_album": False,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def album_remove_song(request, album_id, song_id):
    album = get_object_or_404(Album, id=album_id, user=request.user)
    song = get_object_or_404(Song, id=song_id)

    if song not in album.songs.all():
        return Response(
            {"message": "Song not in album"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    album.songs.remove(song)
    return Response(
        {"message": f"Removed '{song.title}' from album '{album.name}'."}
    )


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


@api_view(["GET"])
@permission_classes([AllowAny])
def search(request):
    query = request.GET.get("query", "").strip()
    genre_id = request.GET.get("genre", "")

    songs = Song.objects.all()
    artists = Artist.objects.none()

    if query:
        songs = songs.filter(title__icontains=query)
        artists = Artist.objects.filter(name__icontains=query)

    selected_genre_obj = None

    if genre_id:
        songs = songs.filter(genres__id=genre_id)
        
        try:
            selected_genre_obj = Genre.objects.get(id=genre_id)
        except Genre.DoesNotExist:
            selected_genre_obj = None

    return Response(
        {
            "songs": SongSerializer(songs.distinct(), many=True, context={"request": request}).data,
            "artists": ArtistSerializer(artists, many=True, context={"request": request}).data,
            "query": query,
            "selected_genre": str(genre_id) if genre_id else "",
            "selected_genre_name": selected_genre_obj.name if selected_genre_obj else "",
        }
    )
