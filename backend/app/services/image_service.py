"""Image upload and processing service."""
import uuid
import logging
from typing import Optional, List, Tuple
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
MAX_FILE_SIZE_MB = 10
THUMBNAIL_SIZES = [(150, 150), (300, 300), (600, 600)]


@dataclass
class ImageMeta:
    id: str
    original_url: str
    thumbnail_url: str
    width: int
    height: int
    size_bytes: int
    mime_type: str
    alt_text: str = ""


class ImageService:
    """Handles image uploads, resizing, and storage."""

    def __init__(self, storage_client, cdn_base_url: str = ""):
        self.storage = storage_client
        self.cdn_base = cdn_base_url

    async def upload(
        self,
        file_data: bytes,
        filename: str,
        user_id: str,
        alt_text: str = "",
    ) -> ImageMeta:
        """Upload and process an image."""
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"File type {ext} not allowed. Use: {ALLOWED_EXTENSIONS}"
            )

        size_mb = len(file_data) / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            raise ValueError(
                f"File too large ({size_mb:.1f}MB). Max: {MAX_FILE_SIZE_MB}MB"
            )

        image_id = str(uuid.uuid4())
        key = f"images/{user_id}/{image_id}{ext}"

        # Upload original
        original_url = await self.storage.upload(key, file_data)

        # Generate thumbnails
        thumbnails = await self._generate_thumbnails(
            file_data, image_id, user_id, ext
        )

        thumbnail_url = thumbnails[0] if thumbnails else original_url
        width, height = self._get_dimensions(file_data)

        return ImageMeta(
            id=image_id,
            original_url=f"{self.cdn_base}/{key}",
            thumbnail_url=thumbnail_url,
            width=width,
            height=height,
            size_bytes=len(file_data),
            mime_type=f"image/{ext.lstrip('.')}",
            alt_text=alt_text,
        )

    async def delete(self, image_id: str, user_id: str) -> bool:
        """Delete an image and its thumbnails."""
        try:
            prefix = f"images/{user_id}/{image_id}"
            await self.storage.delete_prefix(prefix)
            logger.info(f"Deleted image {image_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete image {image_id}: {e}")
            return False

    async def get_gallery(
        self, user_id: str, page: int = 1, per_page: int = 20
    ) -> List[ImageMeta]:
        """Get user's image gallery."""
        prefix = f"images/{user_id}/"
        images = await self.storage.list_objects(prefix)
        start = (page - 1) * per_page
        return images[start:start + per_page]

    async def _generate_thumbnails(
        self,
        file_data: bytes,
        image_id: str,
        user_id: str,
        ext: str,
    ) -> List[str]:
        """Generate thumbnail versions of an image."""
        urls = []
        for width, height in THUMBNAIL_SIZES:
            thumb_key = f"images/{user_id}/{image_id}_thumb_{width}x{height}{ext}"
            try:
                resized = await self._resize(file_data, width, height)
                url = await self.storage.upload(thumb_key, resized)
                urls.append(f"{self.cdn_base}/{thumb_key}")
            except Exception as e:
                logger.warning(f"Thumbnail generation failed for {width}x{height}: {e}")
        return urls

    async def _resize(
        self, data: bytes, width: int, height: int
    ) -> bytes:
        """Resize image to fit within dimensions."""
        # Placeholder for actual image processing (Pillow/wand)
        return data

    def _get_dimensions(self, data: bytes) -> Tuple[int, int]:
        """Extract image dimensions."""
        # Placeholder
        return (0, 0)
