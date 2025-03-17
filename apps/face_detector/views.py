from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from face_detector.forms import ImageUploadForm
from face_detector.tasks import broadcast_image


@csrf_exempt
def upload_image(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                # Save the image
                image_instance = form.save()
                broadcast_image.delay(image_instance.id)

                # Return success response
                response_data = {
                    "status": "success",
                    "message": "Image uploaded successfully",
                    "image_id": image_instance.id,
                    "image_url": image_instance.image.url,
                }
                return JsonResponse(response_data, status=201)

            except Exception as e:
                return JsonResponse(
                    {"status": "error", "message": f"Error saving image: {str(e)}"}, status=500
                )

        else:
            return JsonResponse(
                {"status": "error", "message": "Invalid form data", "errors": form.errors},
                status=400,
            )

    return JsonResponse(
        {"status": "error", "message": "Only POST requests are allowed"}, status=405
    )
