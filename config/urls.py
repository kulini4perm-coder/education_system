from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('materials.urls', namespace='materials')),
    path('users/', include('users.urls', namespace='users')),

    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # Интерфейс Swagger
    path('schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),
    # Альтернативный интерфейс Redoc
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]
