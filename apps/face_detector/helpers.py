import uuid
from typing import Any


def unique_path(folder: str, instance: Any, filename: str) -> str:
    """Generate a unique file path using UUID."""
    ext = filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{ext}"
    return f"{folder}/{unique_filename}"
