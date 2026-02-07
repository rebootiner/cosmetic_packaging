import imghdr
from typing import Any


class ImagePipelineError(ValueError):
    pass


def _parse_dimensions(image_bytes: bytes, image_type: str) -> tuple[int | None, int | None]:
    # PNG: width/height are bytes 16~23 in IHDR
    if image_type == 'png' and len(image_bytes) >= 24:
        width = int.from_bytes(image_bytes[16:20], 'big')
        height = int.from_bytes(image_bytes[20:24], 'big')
        return width, height

    # JPEG: scan SOF marker without external dependencies
    if image_type == 'jpeg' and len(image_bytes) > 4:
        i = 2
        while i + 9 < len(image_bytes):
            if image_bytes[i] != 0xFF:
                i += 1
                continue
            marker = image_bytes[i + 1]
            i += 2
            if marker in (0xD8, 0xD9):
                continue
            if i + 2 > len(image_bytes):
                break
            segment_length = int.from_bytes(image_bytes[i : i + 2], 'big')
            if segment_length < 2 or i + segment_length > len(image_bytes):
                break
            # SOF0~SOF3 and SOF5~SOF7 and SOF9~SOF11 and SOF13~SOF15
            if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
                if i + 7 <= len(image_bytes):
                    height = int.from_bytes(image_bytes[i + 3 : i + 5], 'big')
                    width = int.from_bytes(image_bytes[i + 5 : i + 7], 'big')
                    return width, height
            i += segment_length

    # GIF: little-endian width/height at 6~9
    if image_type == 'gif' and len(image_bytes) >= 10:
        width = int.from_bytes(image_bytes[6:8], 'little')
        height = int.from_bytes(image_bytes[8:10], 'little')
        return width, height

    # WEBP: simple VP8X canvas parse
    if image_type == 'webp' and len(image_bytes) >= 30:
        if image_bytes[12:16] == b'VP8X':
            width = 1 + int.from_bytes(image_bytes[24:27], 'little')
            height = 1 + int.from_bytes(image_bytes[27:30], 'little')
            return width, height

    return None, None


def preprocess_image(image_bytes: bytes) -> dict[str, Any]:
    if not image_bytes:
        raise ImagePipelineError('Empty image payload')

    image_type = imghdr.what(None, h=image_bytes)
    if image_type is None:
        raise ImagePipelineError('Unsupported or invalid image header')

    width, height = _parse_dimensions(image_bytes, image_type)

    return {
        'format': image_type,
        'size_bytes': len(image_bytes),
        'width': width,
        'height': height,
        'header_valid': True,
    }


def segment_image(image_bytes: bytes) -> dict[str, Any]:
    if not image_bytes:
        raise ImagePipelineError('Empty image payload')

    # Dummy segmentation stats based on byte distribution (MVP placeholder)
    sample = image_bytes[: min(len(image_bytes), 4096)]
    high_bytes = sum(1 for b in sample if b >= 128)
    ratio = round(high_bytes / len(sample), 4)

    return {
        'mask_width': 64,
        'mask_height': 64,
        'foreground_ratio': ratio,
        'background_ratio': round(1 - ratio, 4),
        'confidence': 0.5,
        'algorithm': 'mvp-dummy-threshold',
    }
