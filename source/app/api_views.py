from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Song, Artist, Genre, Album
from .serializers import (
    SongSerializer,
    SongWriteSerializer,
    ArtistSerializer,
    GenreSerializer,
    AlbumSerializer,
    UserSerializer,
)


class IndexAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"message": "index api"})


class LoginAPIView(TokenObtainPairView):
    pass


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email", "")

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already taken"}, status=400)

        user = User.objects.create_user(
            username=username, password=password, email=email
        )
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user_id": user.id,
                "message": "Register successfully!"
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


class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)

        return Response(serializer.data)


# Songs
class SongListAPIView(generics.ListAPIView):
    queryset = Song.objects.all().order_by("-created_at")
    serializer_class = SongSerializer
    permission_classes = [AllowAny]


class SongDetailAPIView(generics.RetrieveAPIView):
    queryset = Song.objects.all()
    serializer_class = SongSerializer
    permission_classes = [AllowAny]


class FavoriteSongListAPIView(generics.ListAPIView):
    serializer_class = SongSerializer
    permission_classes = [IsAuthenticated]

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


# Artists
class ArtistListAPIView(generics.ListAPIView):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    permission_classes = [AllowAny]


class ArtistDetailAPIView(generics.RetrieveAPIView):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    permission_classes = [AllowAny]


# GENRES
class GenreListAPIView(generics.ListAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [AllowAny]


class GenreDetailAPIView(generics.RetrieveAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [AllowAny]


# Albums
class AlbumListAPIView(generics.ListCreateAPIView):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AlbumDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AlbumSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Album.objects.filter(user=self.request.user)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def album_add_song(request, album_id, song_id):
    album = get_object_or_404(Album, id=album_id, user=request.user)
    song = get_object_or_404(Song, id=song_id)

    if song in album.songs.all():
        return Response({"message": "Song already in album"}, status=400)

    album.songs.add(song)
    return Response({"message": f"Song '{song.title}' added to album '{album.name}'"})


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def album_remove_song(request, album_id, song_id):
    album = get_object_or_404(Album, id=album_id, user=request.user)
    song = get_object_or_404(Song, id=song_id)

    if song not in album.songs.all():
        return Response({"message": "Song not in album"}, status=400)

    album.songs.remove(song)

    return Response(
        {"message": f"Song '{song.title}' removed from album '{album.name}'"}
    )


# Search
@api_view(["GET"])
def search_songs(request):
    query = request.GET.get("query", "")
    genre_id = request.GET.get("genre", "")

    songs = Song.objects.all()

    if query:
        songs = songs.filter(title__icontains=query)

    if genre_id:
        songs = songs.filter(genres__id=genre_id)

    serializer = SongSerializer(songs, many=True)

    return Response(serializer.data)


########################################
# Admin CRUD (Song, Artist, Genre)
########################################


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)


# SONG Admin CRUD
class AdminSongListCreateAPIView(generics.ListCreateAPIView):
    queryset = Song.objects.all().order_by("-created_at")
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SongWriteSerializer

        return SongSerializer

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class AdminSongDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Song.objects.all()
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return SongWriteSerializer

        return SongSerializer


# ARTIST Admin CRUD
class AdminArtistListCreateAPIView(generics.ListCreateAPIView):
    queryset = Artist.objects.all().order_by("-id")
    serializer_class = ArtistSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class AdminArtistDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


# GENRE Admin CRUD
class AdminGenreListCreateAPIView(generics.ListCreateAPIView):
    queryset = Genre.objects.all().order_by("-id")
    serializer_class = GenreSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class AdminGenreDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
