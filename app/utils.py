import os
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.config import settings


def generate_visitor_id() -> str:
    return "VIS-" + uuid.uuid4().hex[:10].upper()


def _matches_declared_image_type(contents: bytes, extension: str) -> bool:
    """Check the file's actual bytes against its claimed extension.

    A client-supplied extension is just a label — without checking the
    magic bytes, anything could be renamed to ".jpg" and uploaded.
    """
    if extension in (".jpg", ".jpeg"):
        return contents.startswith(b"\xff\xd8\xff")
    if extension == ".png":
        return contents.startswith(b"\x89PNG\r\n\x1a\n")
    if extension == ".webp":
        return contents[:4] == b"RIFF" and contents[8:12] == b"WEBP"
    return False


async def save_photo(photo: UploadFile, directory: str, prefix: str) -> str:
    """Validate and persist an uploaded photo, returning its stored path.

    The filename is regenerated (never taken from the client) to avoid
    path-traversal and overwrite issues from an attacker-controlled name.
    """
    extension = Path(photo.filename or "").suffix.lower()

    if extension not in settings.ALLOWED_PHOTO_EXTENSIONS:
        allowed = ", ".join(sorted(settings.ALLOWED_PHOTO_EXTENSIONS))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported photo type. Allowed types: {allowed}",
        )

    contents = await photo.read()

    max_bytes = settings.MAX_PHOTO_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Photo exceeds the {settings.MAX_PHOTO_SIZE_MB}MB size limit",
        )

    if not _matches_declared_image_type(contents, extension):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File content doesn't match a valid image of its declared type",
        )

    os.makedirs(directory, exist_ok=True)

    safe_name = f"{prefix}_{uuid.uuid4().hex[:8]}{extension}"
    file_path = os.path.join(directory, safe_name)

    with open(file_path, "wb") as f:
        f.write(contents)

    return file_path
