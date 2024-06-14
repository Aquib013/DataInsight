from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
                  path('', views.home, name='home'),
                  path('upload/', views.upload_file, name='upload'),
                  path('analyze/', views.analyze_data, name='analyze_data'),
                  path('visualize/', views.visualize_data, name='visualize_data'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
