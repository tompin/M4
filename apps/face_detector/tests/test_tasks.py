from pathlib import Path
from unittest.mock import patch, MagicMock

from django.core.files.base import ContentFile
from django.test import TestCase

from face_detector.models import UploadedImage
from face_detector.tasks import broadcast_image


class BroadcastImageTaskTest(TestCase):
    def setUp(self):
        # Create a sample UploadedImage instance
        test_file_path = Path(__file__).parent.absolute() / "img" / "img2.jpg"
        self.image_content = open(test_file_path, "rb").read()
        self.uploaded_image = UploadedImage.objects.create(
            image=ContentFile(self.image_content, name="img2.jpg")
        )
        self.channel_layer_mock = MagicMock()
        # Mock detect_and_mark_faces to return a fake image array
        self.fake_image_array = MagicMock()

    # Test 1: Success Case
    @patch("face_detector.tasks.get_channel_layer")
    @patch("face_detector.tasks.async_to_sync")
    @patch("face_detector.tasks.detect_and_mark_faces")
    @patch("face_detector.tasks.cv2.imencode")
    def test_broadcast_image_success(
        self,
        mock_imencode,
        mock_detect,
        mock_async_to_sync,
        mock_get_channel_layer,
    ):
        mock_detect.return_value = self.fake_image_array
        mock_imencode.return_value = (True, MagicMock(tobytes=lambda: b"encoded data"))
        mock_get_channel_layer.return_value = self.channel_layer_mock

        # Run the task
        result = broadcast_image(self.uploaded_image.id)

        self.assertEqual(result, "Image broadcasted successfully")

        # Verify image processing
        mock_detect.assert_called_once_with(self.uploaded_image.image.path)
        mock_imencode.assert_called_once_with(".jpg", self.fake_image_array)

        # Verify database update
        updated_image = UploadedImage.objects.get(id=self.uploaded_image.id)
        self.assertTrue(updated_image.image_with_marked_faces)
        self.assertEqual(updated_image.image_with_marked_faces.name[:9], "processed")

        # Verify WebSocket broadcast
        mock_async_to_sync.assert_called_once_with(self.channel_layer_mock.group_send)

    def test_broadcast_image_does_not_exist(self):
        # Use a non-existent ID
        non_existent_id = 9999
        result = broadcast_image(non_existent_id)

        self.assertEqual(result, f"Image {non_existent_id} doesn't exists")

    @patch("face_detector.tasks.detect_and_mark_faces")
    @patch("face_detector.tasks.cv2.imencode")
    def test_broadcast_image_encoding_failure(self, mock_imencode, mock_detect):
        mock_detect.return_value = self.fake_image_array
        mock_imencode.return_value = (False, None)  # Simulate encoding failure

        # Run the task
        result = broadcast_image(self.uploaded_image.id)

        self.assertEqual(result, "Error broadcasting image: Could not encode image")

        # Verify no save occurred
        updated_image = UploadedImage.objects.get(id=self.uploaded_image.id)
        self.assertFalse(updated_image.image_with_marked_faces)

    @patch("face_detector.tasks.detect_and_mark_faces")
    def test_broadcast_image_generic_exception(self, mock_detect):
        # Simulate an exception (e.g., file not found)
        mock_detect.side_effect = Exception("File not found")

        # Run the task
        result = broadcast_image(self.uploaded_image.id)

        # Assertions
        self.assertEqual(result, "Error broadcasting image: File not found")

        # Verify no save occurred
        updated_image = UploadedImage.objects.get(id=self.uploaded_image.id)
        self.assertFalse(updated_image.image_with_marked_faces)
