import os
import struct
from pathlib import Path
from typing import Tuple, Optional, List
from PIL import Image

from app.config import settings
from app.models.domain import MediaValidationResult

class MediaValidationService:
    @staticmethod
    def validate_file_size(file_size_bytes: int, max_size_mb: float) -> Tuple[bool, Optional[str]]:
        size_mb = file_size_bytes / (1024 * 1024)
        if size_mb > max_size_mb:
            return False, f"File size ({size_mb:.1f} MB) exceeds maximum allowed limit of {max_size_mb:.1f} MB."
        return True, None

    @staticmethod
    def classify_aspect_ratio(width: int, height: int) -> Tuple[str, Optional[str]]:
        """
        Calculates ratio and checks if it matches Instagram standard aspect ratios:
        - 1:1 (Square - 1.0)
        - 4:5 (Portrait - 0.8)
        - 1.91:1 (Landscape - 1.91)
        """
        if height == 0:
            return "unknown", "Invalid image height."

        ratio = width / height

        # Target ratios: 1:1 (1.0), 4:5 (0.8), 1.91:1 (~1.91)
        if abs(ratio - 1.0) <= 0.05:
            return "1:1", None
        elif abs(ratio - 0.8) <= 0.05:
            return "4:5", None
        elif abs(ratio - 1.91) <= 0.08:
            return "1.91:1", None
        else:
            ratio_str = f"{ratio:.2f}:1"
            warning = (
                f"Image aspect ratio ({ratio_str}) differs from Instagram standard ratios "
                f"(1:1 square, 4:5 portrait, 1.91:1 landscape). Image may be cropped or padded when posted."
            )
            return ratio_str, warning

    @staticmethod
    def _estimate_video_duration(file_path: Path) -> Optional[float]:
        """
        Parses MP4/MOV container headers (mvhd atom) to extract duration without external heavy dependencies.
        Returns duration in seconds if readable, else None.
        """
        try:
            with open(file_path, "rb") as f:
                data = f.read(1000000)  # read first 1MB for header
                mvhd_pos = data.find(b"mvhd")
                if mvhd_pos != -1:
                    version = data[mvhd_pos + 4]
                    if version == 0:
                        timescale, duration = struct.unpack(">II", data[mvhd_pos + 16 : mvhd_pos + 24])
                    elif version == 1:
                        timescale, duration = struct.unpack(">IQ", data[mvhd_pos + 20 : mvhd_pos + 32])
                    else:
                        return None
                    if timescale > 0:
                        return float(duration) / float(timescale)
        except Exception:
            pass
        return None

    @classmethod
    def validate_image(
        cls,
        file_path: Path,
        filename: str,
        mime_type: Optional[str] = None
    ) -> MediaValidationResult:
        errors: List[str] = []
        warnings: List[str] = []

        if not file_path.exists():
            return MediaValidationResult(
                is_valid=False,
                media_type="image",
                mime_type=mime_type or "image/jpeg",
                file_size_mb=0,
                errors=["File does not exist."]
            )

        file_size_bytes = file_path.stat().st_size
        file_size_mb = file_size_bytes / (1024 * 1024)

        # 1. Size check
        ok_size, err_size = cls.validate_file_size(file_size_bytes, settings.INSTAGRAM_MAX_IMAGE_SIZE_MB)
        if not ok_size and err_size:
            errors.append(err_size)

        # 2. Open image with PIL
        width, height = None, None
        aspect_ratio_name = None
        format_mime = mime_type or "image/jpeg"

        try:
            with Image.open(file_path) as img:
                width, height = img.size
                if hasattr(Image, "MIME") and img.format in Image.MIME:
                    format_mime = Image.MIME[img.format]

                # Format check
                ext = Path(filename).suffix.lower()
                allowed_exts = [".jpg", ".jpeg", ".png", ".webp"]
                if ext not in allowed_exts and format_mime not in settings.INSTAGRAM_ALLOWED_IMAGE_FORMATS:
                    errors.append(f"Unsupported image format ({ext or format_mime}). Allowed: JPEG, PNG, WEBP.")

                # Resolution check
                if width < 320 or height < 320:
                    warnings.append(f"Image resolution ({width}x{height}px) is below Instagram recommended minimum of 320x320px.")

                # Aspect ratio check
                aspect_ratio_name, aspect_warning = cls.classify_aspect_ratio(width, height)
                if aspect_warning:
                    warnings.append(aspect_warning)

        except Exception as e:
            errors.append(f"Failed to process image file: {str(e)}")

        is_valid = len(errors) == 0

        return MediaValidationResult(
            is_valid=is_valid,
            media_type="image",
            mime_type=format_mime,
            file_size_mb=round(file_size_mb, 2),
            width=width,
            height=height,
            aspect_ratio=aspect_ratio_name,
            warnings=warnings,
            errors=errors
        )

    @classmethod
    def validate_video(
        cls,
        file_path: Path,
        filename: str,
        mime_type: Optional[str] = None
    ) -> MediaValidationResult:
        errors: List[str] = []
        warnings: List[str] = []

        if not file_path.exists():
            return MediaValidationResult(
                is_valid=False,
                media_type="video",
                mime_type=mime_type or "video/mp4",
                file_size_mb=0,
                errors=["File does not exist."]
            )

        file_size_bytes = file_path.stat().st_size
        file_size_mb = file_size_bytes / (1024 * 1024)

        # 1. Size check
        ok_size, err_size = cls.validate_file_size(file_size_bytes, settings.INSTAGRAM_MAX_VIDEO_SIZE_MB)
        if not ok_size and err_size:
            errors.append(err_size)

        # 2. Format check
        ext = Path(filename).suffix.lower()
        if ext not in [".mp4", ".mov"] and (mime_type and mime_type not in settings.INSTAGRAM_ALLOWED_VIDEO_FORMATS):
            errors.append(f"Unsupported video format ({ext}). Instagram requires MP4 or MOV format.")

        # 3. Duration check
        duration = cls._estimate_video_duration(file_path)
        if duration is not None:
            if duration > settings.INSTAGRAM_MAX_VIDEO_DURATION_SECONDS:
                errors.append(f"Video duration ({duration:.1f}s) exceeds maximum allowed limit of {settings.INSTAGRAM_MAX_VIDEO_DURATION_SECONDS} seconds (Reel limit).")
            elif duration > 60:
                warnings.append(f"Video is {duration:.1f}s long. Videos over 60s will be posted as an Instagram Reel.")
        else:
            warnings.append("Could not extract exact video duration. Ensure video duration is under 90 seconds.")

        is_valid = len(errors) == 0

        return MediaValidationResult(
            is_valid=is_valid,
            media_type="video",
            mime_type=mime_type or ("video/mp4" if ext == ".mp4" else "video/quicktime"),
            file_size_mb=round(file_size_mb, 2),
            duration_seconds=round(duration, 1) if duration else None,
            warnings=warnings,
            errors=errors
        )
