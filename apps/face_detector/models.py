from functools import partial

from django.db import models

from face_detector.helpers import unique_path


class UploadedImage(models.Model):
    image = models.ImageField(upload_to=partial(unique_path, "uploads"))
    image_with_marked_faces = models.ImageField(
        upload_to=partial(unique_path, "processed"), blank=True, null=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image uploaded at {self.uploaded_at}"
