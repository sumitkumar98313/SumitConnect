from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


# main project urls - connects to accounts app urls
urlpatterns = [
    # django admin panel
    path('admin/', admin.site.urls),

    # all accounts app urls (home, feed, profile etc)
    path('', include('accounts.urls')),
]

# serve media and static files in development mode
# in production these are handled by the web server (like nginx)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
