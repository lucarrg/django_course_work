from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import os  # для STATICFILES_DIRS и раздачи статики

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('coworking.urls')),        # веб-страницы
    path('api/', include('coworking.api_urls')), # API DRF
    path('accounts/', include('accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(settings.BASE_DIR, 'static'))
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
