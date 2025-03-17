from pathlib import Path
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from face_detector.models import UploadedImage


class UploadImageViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("upload_image")
        test_file_path = Path(__file__).parent.absolute() / "img" / "img1.jpg"
        self.image_content = open(test_file_path, "rb").read()
        self.image = SimpleUploadedFile(
            "test_image.jpg", self.image_content, content_type="image/jpeg"
        )
        self.maxDiff = None

    @patch("face_detector.views.broadcast_image.delay")  # Mock Celery task
    def test_upload_image_success(self, mock_broadcast):
        response = self.client.post(self.url, {"image": self.image})

        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertEqual(response_data["status"], "success")
        self.assertEqual(response_data["message"], "Image uploaded successfully")
        self.assertIn("image_id", response_data)
        self.assertIn("image_url", response_data)

        # Verify image was saved
        image_instance = UploadedImage.objects.get(id=response_data["image_id"])
        self.assertTrue(image_instance.image)

        # Verify Celery task was called
        self.assertTrue(mock_broadcast.assert_called_once)

    # Test 2: Invalid Method (GET instead of POST)
    def test_upload_image_invalid_method(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 405)
        response_data = response.json()
        self.assertEqual(response_data["status"], "error")
        self.assertEqual(response_data["message"], "Only POST requests are allowed")

    # Test 3: Invalid Form Data
    def test_upload_image_invalid_form(self):
        # Send POST with no image (invalid form)
        response = self.client.post(
            self.url,
            data={},
        )

        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertEqual(response_data["status"], "error")
        self.assertEqual(response_data["message"], "Invalid form data")
        self.assertIn("errors", response_data)
        self.assertIn("image", response_data["errors"])

    @patch("face_detector.forms.ImageUploadForm.save")
    def test_upload_image_save_error(self, mock_save):
        # Simulate an exception during save
        mock_save.side_effect = Exception("Database error")

        # Prepare POST data with a valid image
        data = {"image": self.image}

        response = self.client.post(
            self.url,
            data=data,
        )

        self.assertEqual(response.status_code, 500)
        response_data = response.json()
        self.assertEqual(response_data["status"], "error")
        self.assertEqual(response_data["message"], "Error saving image: Database error")
