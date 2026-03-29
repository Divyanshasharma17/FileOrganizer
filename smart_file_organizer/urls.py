from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('organizer_app.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# The static() helper serves uploaded files during development (DEBUG=True).
# In production, your web server (nginx/apache) should serve MEDIA_ROOT directly.
