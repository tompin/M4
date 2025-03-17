import os

import cv2
from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from django.core.files.base import ContentFile

from face_detector.face_detection import detect_and_mark_faces
from face_detector.models import UploadedImage


@shared_task
def broadcast_image(image_id: int):
    """
    Celery task to broadcast an image to WebSocket clients
    """
    try:
        uploaded_image = UploadedImage.objects.get(pk=image_id)
        image_with_marked_faces = detect_and_mark_faces(uploaded_image.image.path)
        ext = os.path.splitext(uploaded_image.image.name)[-1].lower()
        success, buffer = cv2.imencode(ext, image_with_marked_faces)
        if not success:
            raise ValueError("Could not encode image")

        uploaded_image.image_with_marked_faces = ContentFile(
            content=buffer.tobytes(),
            name=uploaded_image.image.name,
        )
        uploaded_image.save(update_fields=["image_with_marked_faces"])

        channel_layer = get_channel_layer()

        # Send message to the group
        async_to_sync(channel_layer.group_send)(
            "image_broadcast_group",
            {
                "type": "image_message",
                "image_url": uploaded_image.image_with_marked_faces.url,
            },
        )
        return f"Image broadcasted successfully"

    except UploadedImage.DoesNotExist:
        return f"Image {image_id} doesn't exists"
    except Exception as e:
        return f"Error broadcasting image: {str(e)}"
