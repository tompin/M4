from pathlib import Path
from typing import List, Tuple

import cv2
from mtcnn import MTCNN


def read_image(image_path: Path) -> cv2.Mat:
    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError("Image not found or invalid file path")
    return image


def detect_faces(image: cv2.Mat) -> List[Tuple[int, int, int, int]]:
    detector = MTCNN()
    faces = detector.detect_faces(image)
    return [face["box"] for face in faces]  # Return bounding box coordinates


def mark_boxes(image: cv2.Mat, face_boxes: List[Tuple[int, int, int, int]]) -> cv2.Mat:
    for x, y, w, h in face_boxes:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)

    return image


def detect_and_mark_faces(image_path: Path) -> cv2.Mat:
    image = read_image(image_path)
    face_boxes = detect_faces(image)
    image_with_marked_faces = mark_boxes(image, face_boxes)
    return image_with_marked_faces