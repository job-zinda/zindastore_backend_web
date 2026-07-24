from django.http import JsonResponse
from django.utils import timezone

# Create your views here.

def health(request):
    """Simple health check endpoint"""
    return JsonResponse({
        "status": "ok",
        "app": "zinda_store",
        "time": timezone.now().isoformat(),
    })
