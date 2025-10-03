from .models import Genre


# Global data
def global_data(request):
    return {
        "genres": Genre.objects.all(),
    }
