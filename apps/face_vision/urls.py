from django.conf import settings
from django.conf.urls.static import static

from face_detector.urls import (
    urlpatterns as face_detector_urls,
    websocket_urlpatterns as face_detector_websocket_urls,
)

urlpatterns = (
    face_detector_urls
    + face_detector_websocket_urls
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)
