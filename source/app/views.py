from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404

from .forms import RegisterForm, AlbumForm
from .models import Song, Album, Genre, Artist


def index(request):
    songs = Song.objects.all().order_by("-id")[:5]  # Display newest
    artists = Artist.objects.all().order_by("-id")[:5]  # Display newest

    return render(request, "index.html", {"songs": songs, "artists": artists})


# User
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Register successfully.")

            return redirect("login")
        else:
            messages.error(request, "Register failed.")

    else:
        form = RegisterForm()

    return render(request, "app/user/register.html", {"form": form})


def login_view(request):
    # Check User Login
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)

            return redirect("/")
        else:
            messages.error(request, "Login failed.")

    return render(request, "app/user/login.html")


def logout_view(request):
    auth_logout(request)
    messages.success(request, "Logout successfully.")

    return redirect("login")


@login_required()
def profile(request):
    return render(request, "app/user/index.html")


@login_required()
def favorite_songs(request):
    favorite_songs = request.user.favorite_songs.all()

    return render(
        request, "app/user/favorite.html", {"favorite_songs": favorite_songs}
    )


# Songs
def songs(request):
    songs = Song.objects.all().order_by("-id")[:5]  # Display newest
    artists = Artist.objects.all().order_by("-id")[:5]  # Display newest

    return render(request, "app/song/index.html", {"songs": songs, "artists": artists})


@login_required
def album_detail(request, album_id):
    album = Album.objects.get(id=album_id, user=request.user)

    return render(request, "app/album/detail.html", {"album": album})


# Song
@login_required
def song_detail(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    albums = Album.objects.filter(user=request.user)

    return render(request, "app/song/detail.html", {"song": song, "albums": albums})


@login_required
def song_to_favorite(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    user = request.user

    if song in user.favorite_songs.all():
        user.favorite_songs.remove(song)
        is_favorite = False  # JavaScript
    else:
        user.favorite_songs.add(song)
        is_favorite = True  # JavaScript

    # Return JSON if request is AJAX (JavaScript)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"is_favorite": is_favorite})

    return redirect("/")


@login_required
def song_to_album(request, song_id):
    if request.method == "POST":
        song = get_object_or_404(Song, id=song_id)
        album_id = request.POST.get("album_id")
        album = get_object_or_404(Album, id=album_id, user=request.user)

        if song in album.songs.all():
            messages.info(
                request, f"'{song.title}' is already in the Album '{album.name}'."
            )
        else:
            album.songs.add(song)
            messages.success(
                request, f"'{song.title}' was added to Album '{album.name}'."
            )

        return redirect("song_detail", song_id=song.id)


# Album
@login_required()
def albums(request):
    albums = Album.objects.filter(user=request.user)

    return render(request, "app/album/index.html", {"albums": albums})


@login_required
def album_detail(request, album_id):
    album = Album.objects.get(id=album_id, user=request.user)

    return render(request, "app/album/detail.html", {"album": album})


@login_required
def album_create(request):
    if request.method == "POST":
        form = AlbumForm(request.POST)

        if form.is_valid():
            album = form.save(commit=False)
            album.user = request.user
            album.save()
            form.save_m2m()
            messages.success(
                request, f"Album '{album.name}' Created successfully."
            )

            return redirect("albums")
    else:
        form = AlbumForm()

    return render(request, "app/album/create.html", {"form": form})


@login_required
def album_delete(request, album_id):
    album = get_object_or_404(Album, id=album_id, user=request.user)
    album.delete()
    messages.success(
        request, f"Album '{album.name}' Deleted."
    )

    return redirect("albums")


@login_required
def album_remove_song(request, album_id, song_id):
    album = get_object_or_404(Album, id=album_id, user=request.user)
    song = get_object_or_404(Song, id=song_id)

    album.songs.remove(song)
    messages.success(
        request, f"Removed '{song.title}' from Album '{album.name}'."
    )

    return redirect("album_detail", album_id=album.id)


# Artist
def artists(request):
    artists = Artist.objects.all().order_by("-id")[:5]

    return render(request, "app/artist/index.html", {"artists": artists})


@login_required
def artist_detail(request, artist_id):
    artist = get_object_or_404(Artist, id=artist_id)
    songs = Song.objects.filter(artist=artist).order_by("-id")

    return render(request, "app/artist/detail.html", {"artist": artist, "songs": songs})


# Search
def search(request):
    query = request.GET.get("query")
    genre_id = request.GET.get("genre")

    songs = Song.objects.all()
    artists = Artist.objects.all()

    if query:
        songs = songs.filter(title__icontains=query)
        artists = artists.filter(name__icontains=query)

    selected_genre_obj = None
    if genre_id:
        # Support ManyToMany genres
        songs = songs.filter(genres__id=genre_id)
        try:
            selected_genre_obj = Genre.objects.get(id=genre_id)
        except Genre.DoesNotExist:
            selected_genre_obj = None


    context = {
        # Data
        "songs": songs,
        "artists": artists,
        # User input
        "query": query,
        "selected_genre": str(genre_id),
        "selected_genre_name": selected_genre_obj.name if selected_genre_obj else "",
    }

    return render(request, "app/song/search.html", context)
