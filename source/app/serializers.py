from django.contrib.auth.models import User
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

    class Meta:
        model = Album
        fields = ["id", "name", "songs", "created_at"]


class UserSerializer(serializers.ModelSerializer):
    favorite_songs = SongSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "favorite_songs"]
