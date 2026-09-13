from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. Main API Endpoints (checkout, cart, products മുതലായവ ഇതിലേക്ക് പോകും)
    path('api/', include('api.urls')),
    
    # 2. Core Endpoints (health check പോലുള്ളവയ്ക്ക്)
    path('api/core/', include('core.urls')),
    
    # 3. CMS Endpoints (banners, pages മുതലായവ)
    path('api/cms/', include('cms.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)