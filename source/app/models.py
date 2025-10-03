from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models


class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Artist(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to="artists/", null=True, blank=True)

    def __str__(self):
        return self.name


class Song(models.Model):
    title = models.CharField(max_length=255)
    cover_image = models.ImageField(upload_to="covers/", null=True, blank=True)
    audio_file = models.FileField(
        upload_to="songs/",
        validators=[FileExtensionValidator(allowed_extensions=["mp3"])],
    )
    lyrics = models.TextField(blank=True)

    artist = models.ForeignKey(
        Artist, on_delete=models.SET_NULL, null=True, related_name="songs"
    )
    genres = models.ManyToManyField(Genre, blank=True, related_name="songs")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.artist.name if self.artist else 'Unknown Artist'}"


class Album(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    songs = models.ManyToManyField(Song, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.user.username}"


User.add_to_class(
    "favorite_songs",
    models.ManyToManyField(Song, related_name="favorited_by", blank=True),
)
