from django.urls import path, re_path
from face_detector import views
from face_detector import consumers

websocket_urlpatterns = [
    re_path(r"ws/faces/$", consumers.ImageConsumer.as_asgi()),
]

urlpatterns = [
    path("upload-image/", views.upload_image, name="upload_image"),
]
