from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from billboards import views as billboard_views

urlpatterns = [
    path('admin/logout/', billboard_views.logout_view, name='admin_logout'),
    path('admin/', admin.site.urls),
    path('', include('billboards.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
