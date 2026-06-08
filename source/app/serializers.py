from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers

from .models import Song, Artist, Genre, Album


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name", "description"]


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ["id", "name", "bio", "image"]


class SongSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True)
    genres = GenreSerializer(many=True, read_only=True)
    uploaded_by_name = serializers.CharField(
        source="uploaded_by.username",
        read_only=True
    )

    class Meta:
        model = Song
        fields = [
            "id",
            "title",
            "cover_image",
            "audio_file",
            "lyrics",
            "artist",
            "genres",
            "uploaded_by",
            "uploaded_by_name",
            "created_at",
        ]


class SongWriteSerializer(serializers.ModelSerializer):
    artist_id = serializers.PrimaryKeyRelatedField(
        queryset=Artist.objects.all(), source="artist", allow_null=True, required=False
    )
    genre_ids = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(), many=True, source="genres", required=False
    )

    class Meta:
        model = Song
        fields = [
            "id",
            "title",
            "cover_image",
            "audio_file",
            "lyrics",
            "artist_id",
            "genre_ids",
        ]

    def create(self, validated_data):
        genres = validated_data.pop("genres", [])
        song = Song.objects.create(**validated_data)
        if genres:
            song.genres.set(genres)
        return song

    def update(self, instance, validated_data):
        genres = validated_data.pop("genres", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if genres is not None:
            instance.genres.set(genres)
        return instance


class AlbumSerializer(serializers.ModelSerializer):
    songs = SongSerializer(many=True, read_only=True)
    song_ids = serializers.PrimaryKeyRelatedField(
        queryset=Song.objects.all(),
        many=True,
        source="songs",
        write_only=True,
        required=False,
    )

    class Meta:
        model = Album
        fields = ["id", "name", "songs", "song_ids", "created_at"]

    def create(self, validated_data):
        songs = validated_data.pop("songs", [])
        album = Album.objects.create(**validated_data)
        if songs:
            album.songs.set(songs)
        return album


class UserSerializer(serializers.ModelSerializer):
    favorite_songs = SongSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "favorite_songs"]


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
        validators=[UnicodeUsernameValidator()],
    )
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False, allow_blank=True, default="")

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "A user with that username already exists."
            )
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password2": ["The two password fields didn’t match."]}
            )

        user = User(
            username=attrs["username"],
            email=attrs.get("email", ""),
        )
        validate_password(attrs["password"], user)
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        return User.objects.create_user(**validated_data)
