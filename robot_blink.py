#!/usr/bin/env pybricks-micropython
"""Pybricks GIF renderer for the 5x5 LED matrix.

This script can play animated GIFs by scaling each frame down to the hub's
5x5 matrix and mapping pixel intensity to LED brightness. If no GIF is
available, it falls back to the classic blinking robot animation.
"""

try:
    import os  # type: ignore
except ImportError:  # pragma: no cover - MicroPython hubs may not provide os
    os = None  # type: ignore[assignment]

from pybricks.hubs import PrimeHub
from pybricks.tools import Matrix, wait

try:
    from PIL import Image, ImageSequence  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - handled gracefully at runtime
    Image = None  # type: ignore
    ImageSequence = None  # type: ignore


# Global configuration
FRAME_SIZE = (5, 5)
MAX_BRIGHTNESS = 100
FPS = 5
GIF_ENV_VAR = "PYBRICKS_GIF"
DEFAULT_GIF_CANDIDATES = ["robot_animation.gif", "giphy-downsized.gif"]
EMBEDDED_SENTINEL = "__embedded__"
EMBEDDED_SOURCE = "giphy-downsized.gif"
EMBEDDED_FPS = 5
EMBEDDED_FRAMES_DATA = [
    [[48, 48, 48, 48, 48], [48, 95, 28, 48, 48], [48, 40, 97, 48, 48], [48, 48, 48, 48, 48], [48, 49, 48, 72, 2]],
    [[48, 48, 48, 48, 48], [48, 48, 48, 44, 48], [48, 48, 98, 48, 48], [48, 49, 48, 48, 48], [49, 48, 91, 44, 44]],
    [[48, 48, 48, 48, 48], [48, 48, 48, 96, 48], [48, 48, 96, 48, 48], [48, 0, 48, 48, 48], [48, 48, 95, 41, 49]],
    [[48, 48, 48, 20, 48], [48, 48, 48, 97, 48], [48, 48, 96, 96, 48], [48, 4, 48, 48, 48], [48, 49, 98, 7, 55]],
    [[48, 48, 48, 0, 48], [48, 48, 96, 96, 48], [48, 48, 96, 96, 48], [48, 48, 48, 48, 48], [48, 48, 95, 7, 54]],
    [[48, 48, 48, 0, 48], [48, 48, 98, 96, 48], [48, 48, 96, 0, 48], [48, 48, 48, 48, 48], [47, 49, 99, 2, 54]],
    [[48, 48, 24, 91, 48], [48, 48, 48, 96, 48], [48, 48, 96, 42, 48], [48, 48, 48, 49, 48], [49, 48, 99, 27, 15]],
    [[48, 91, 48, 48, 48], [48, 96, 48, 48, 48], [48, 79, 96, 48, 48], [48, 48, 48, 48, 48], [49, 48, 95, 20, 7]],
    [[48, 48, 48, 48, 48], [48, 96, 48, 48, 48], [48, 98, 96, 48, 48], [48, 48, 48, 48, 48], [52, 48, 36, 55, 4]],
    [[48, 96, 48, 48, 48], [48, 69, 48, 48, 48], [48, 96, 96, 48, 48], [48, 48, 48, 48, 48], [96, 50, 12, 23, 7]],
    [[48, 7, 48, 48, 48], [48, 97, 96, 48, 48], [48, 96, 96, 48, 48], [48, 48, 48, 48, 47], [51, 51, 99, 16, 56]],
    [[48, 95, 48, 48, 48], [48, 95, 49, 48, 48], [48, 1, 94, 48, 48], [48, 48, 48, 48, 48], [48, 49, 99, 23, 49]],
    [[48, 48, 48, 48, 48], [48, 48, 48, 44, 48], [48, 48, 97, 48, 48], [48, 48, 48, 48, 48], [48, 49, 99, 36, 35]],
    [[48, 48, 48, 48, 48], [48, 48, 48, 94, 48], [48, 48, 95, 2, 48], [48, 26, 49, 48, 48], [48, 48, 94, 24, 11]],
    [[48, 48, 48, 96, 48], [48, 48, 48, 96, 48], [48, 48, 96, 96, 48], [48, 48, 48, 48, 48], [49, 50, 99, 53, 11]],
    [[48, 48, 48, 4, 48], [48, 48, 96, 96, 48], [48, 48, 96, 96, 48], [48, 48, 48, 48, 48], [55, 48, 99, 56, 4]],
    [[48, 48, 48, 99, 48], [48, 48, 48, 96, 48], [48, 48, 96, 16, 48], [48, 48, 48, 48, 48], [52, 48, 99, 62, 4]],
    [[48, 48, 3, 97, 48], [48, 48, 48, 96, 48], [48, 48, 96, 0, 48], [48, 41, 48, 48, 48], [48, 48, 97, 75, 71]],
    [[48, 97, 48, 48, 48], [48, 96, 48, 48, 48], [48, 96, 96, 48, 48], [48, 48, 48, 48, 48], [50, 48, 97, 66, 43]],
    [[48, 48, 48, 48, 48], [48, 96, 48, 48, 48], [48, 96, 97, 48, 48], [48, 48, 48, 48, 48], [0, 0, 0, 0, 0]],
    [[48, 97, 48, 48, 48], [48, 96, 98, 48, 48], [48, 96, 95, 48, 48], [48, 48, 47, 49, 48], [47, 48, 98, 66, 20]],
    [[48, 0, 48, 48, 48], [48, 96, 11, 48, 48], [48, 95, 96, 48, 48], [48, 48, 48, 48, 48], [48, 48, 96, 41, 75]],
    [[48, 96, 48, 48, 48], [48, 96, 49, 48, 48], [48, 50, 96, 48, 48], [48, 50, 48, 48, 48], [48, 48, 97, 69, 59]],
    [[48, 48, 48, 0, 48], [48, 48, 48, 99, 48], [48, 48, 96, 48, 48], [48, 48, 48, 48, 48], [48, 48, 97, 16, 11]],
    [[48, 48, 48, 0, 48], [48, 48, 48, 95, 48], [48, 48, 97, 95, 48], [48, 0, 48, 48, 48], [49, 48, 99, 20, 22]],
    [[48, 48, 48, 4, 48], [48, 48, 7, 96, 48], [48, 48, 98, 0, 48], [48, 48, 48, 48, 48], [54, 48, 95, 39, 35]],
    [[48, 48, 48, 0, 48], [48, 48, 96, 96, 48], [48, 48, 96, 13, 48], [48, 48, 48, 48, 48], [52, 48, 97, 75, 32]],
    [[48, 48, 48, 97, 48], [48, 48, 47, 94, 48], [48, 48, 96, 16, 48], [48, 48, 48, 48, 48], [48, 48, 99, 22, 54]],
    [[48, 48, 48, 32, 48], [48, 48, 96, 96, 48], [48, 48, 70, 48, 48], [48, 48, 48, 48, 48], [48, 49, 96, 55, 27]],
    [[48, 48, 48, 4, 48], [48, 96, 96, 0, 48], [48, 48, 70, 48, 48], [48, 48, 48, 48, 48], [48, 48, 98, 55, 7]],
    [[48, 48, 1, 48, 48], [48, 48, 32, 49, 48], [48, 48, 96, 48, 48], [48, 48, 48, 48, 48], [48, 48, 88, 49, 2]],
    [[48, 0, 48, 48, 48], [48, 48, 96, 48, 48], [48, 48, 0, 48, 48], [48, 48, 48, 48, 48], [49, 48, 15, 49, 7]],
    [[48, 29, 0, 48, 48], [48, 48, 96, 96, 48], [48, 48, 73, 48, 48], [48, 48, 48, 48, 48], [49, 48, 91, 52, 49]],
    [[48, 48, 97, 48, 48], [48, 48, 97, 48, 48], [48, 48, 96, 48, 48], [48, 48, 48, 48, 48], [50, 48, 10, 56, 4]],
    [[48, 48, 99, 48, 48], [48, 48, 48, 48, 48], [48, 48, 99, 48, 48], [48, 48, 4, 48, 48], [48, 48, 88, 51, 49]],
    [[48, 48, 0, 48, 48], [48, 48, 48, 48, 48], [48, 48, 95, 48, 48], [48, 48, 48, 48, 48], [48, 48, 96, 32, 27]],
    [[48, 48, 48, 49, 48], [48, 48, 48, 96, 48], [48, 48, 95, 49, 48], [48, 27, 48, 48, 48], [48, 48, 96, 66, 49]],
    [[48, 48, 48, 7, 48], [48, 48, 0, 96, 48], [48, 48, 96, 96, 48], [48, 48, 48, 48, 48], [51, 48, 71, 27, 26]],
    [[48, 48, 47, 99, 48], [48, 48, 48, 99, 48], [48, 48, 99, 95, 48], [48, 48, 48, 48, 48], [48, 49, 97, 17, 20]],
    [[48, 95, 48, 48, 48], [48, 96, 48, 48, 48], [48, 97, 96, 48, 48], [48, 48, 48, 48, 48], [49, 48, 99, 36, 4]],
    [[48, 96, 48, 48, 48], [48, 96, 48, 48, 48], [48, 95, 95, 48, 48], [48, 48, 48, 49, 48], [49, 48, 99, 59, 4]],
    [[48, 94, 48, 48, 48], [48, 75, 2, 48, 48], [48, 97, 96, 48, 48], [48, 48, 15, 48, 48], [51, 48, 96, 75, 73]],
    [[48, 7, 48, 48, 48], [48, 97, 96, 48, 48], [48, 96, 96, 48, 48], [48, 48, 48, 48, 48], [31, 49, 97, 73, 11]],
    [[48, 97, 48, 48, 48], [48, 96, 48, 48, 48], [48, 1, 96, 48, 48], [48, 48, 48, 48, 48], [50, 49, 99, 43, 43]],
    [[0, 48, 48, 95, 0], [48, 48, 48, 96, 48], [48, 48, 94, 49, 48], [48, 48, 48, 0, 0], [0, 0, 0, 0, 0]],
    [[48, 48, 48, 97, 48], [48, 48, 48, 96, 48], [48, 48, 95, 48, 48], [48, 4, 48, 48, 48], [49, 48, 99, 62, 27]],
    [[48, 48, 48, 96, 48], [48, 48, 49, 96, 48], [48, 48, 96, 96, 48], [48, 48, 48, 48, 48], [42, 48, 99, 66, 4]],
    [[48, 48, 48, 7, 48], [48, 48, 97, 99, 48], [48, 48, 95, 94, 48], [48, 48, 48, 48, 48], [17, 48, 95, 56, 2]],
    [[48, 48, 48, 96, 48], [48, 48, 49, 96, 48], [48, 48, 96, 11, 48], [48, 48, 48, 48, 48], [50, 51, 99, 64, 7]],
    [[48, 97, 48, 48, 48], [48, 96, 48, 48, 48], [48, 99, 97, 48, 48], [48, 48, 48, 48, 48], [49, 49, 97, 24, 20]],
    [[48, 97, 48, 48, 48], [48, 96, 48, 48, 48], [48, 97, 97, 48, 48], [48, 48, 48, 48, 48], [47, 48, 97, 36, 27]],
    [[48, 97, 48, 48, 48], [48, 96, 48, 48, 48], [48, 95, 97, 48, 48], [48, 48, 48, 48, 48], [49, 48, 97, 75, 44]],
    [[48, 96, 48, 48, 48], [48, 84, 95, 48, 48], [48, 96, 98, 48, 48], [48, 48, 48, 48, 48], [48, 48, 97, 21, 49]],
    [[48, 0, 48, 48, 48], [48, 96, 99, 48, 48], [48, 97, 95, 48, 48], [48, 48, 48, 48, 48], [49, 49, 97, 69, 2]],
    [[48, 48, 48, 50, 48], [48, 48, 48, 48, 48], [48, 48, 96, 48, 48], [48, 48, 48, 48, 48], [49, 47, 96, 43, 2]],
    [[48, 48, 48, 49, 48], [48, 48, 48, 95, 48], [48, 48, 95, 48, 48], [48, 32, 48, 48, 48], [48, 48, 94, 39, 4]],
    [[48, 48, 48, 7, 48], [48, 48, 48, 95, 48], [48, 48, 97, 98, 48], [48, 1, 48, 48, 48], [49, 48, 99, 22, 49]],
    [[48, 48, 48, 5, 48], [48, 48, 49, 94, 48], [48, 48, 94, 96, 48], [48, 48, 48, 48, 48], [49, 48, 55, 32, 48]],
    [[48, 48, 48, 0, 48], [48, 48, 96, 96, 48], [48, 48, 95, 27, 48], [48, 48, 48, 48, 48], [55, 48, 97, 43, 2]],
    [[48, 48, 0, 97, 48], [48, 48, 48, 96, 48], [48, 48, 95, 1, 48], [48, 48, 48, 48, 48], [47, 48, 95, 73, 4]],
    [[48, 94, 48, 48, 48], [48, 96, 48, 50, 48], [48, 97, 97, 48, 48], [48, 48, 48, 48, 48], [49, 48, 94, 49, 51]],
    [[48, 48, 48, 48, 48], [48, 97, 48, 48, 48], [48, 97, 96, 48, 48], [48, 48, 48, 48, 48], [51, 48, 99, 17, 46]],
    [[48, 96, 48, 48, 48], [48, 96, 48, 48, 48], [48, 94, 96, 48, 48], [48, 48, 48, 48, 48], [51, 48, 96, 43, 51]],
    [[48, 4, 48, 48, 48], [48, 96, 96, 48, 48], [48, 95, 96, 48, 48], [48, 48, 48, 48, 48], [55, 48, 95, 72, 66]],
    [[48, 8, 48, 48, 48], [48, 96, 48, 48, 48], [48, 95, 96, 48, 48], [48, 48, 48, 48, 48], [49, 48, 97, 75, 73]],
    [[48, 53, 48, 48, 48], [48, 97, 49, 48, 48], [48, 99, 96, 48, 48], [48, 48, 48, 48, 48], [47, 48, 97, 62, 7]],
    [[48, 97, 48, 48, 48], [48, 97, 48, 48, 48], [48, 27, 95, 48, 48], [48, 48, 48, 48, 48], [48, 48, 96, 49, 4]],
    [[48, 99, 48, 48, 48], [48, 96, 48, 48, 48], [48, 0, 96, 48, 48], [48, 48, 48, 48, 48], [49, 48, 96, 73, 75]],
    [[48, 99, 48, 48, 48], [48, 96, 48, 48, 48], [48, 98, 96, 48, 48], [48, 48, 48, 48, 48], [48, 49, 95, 71, 62]],
    [[0, 96, 0, 0, 0], [48, 98, 48, 48, 48], [48, 95, 0, 48, 48], [48, 48, 48, 48, 48], [0, 0, 0, 0, 44]],
    [[48, 98, 48, 48, 48], [48, 95, 48, 48, 48], [48, 97, 96, 48, 48], [48, 48, 50, 48, 48], [55, 48, 98, 73, 27]],
    [[48, 2, 48, 48, 51], [48, 96, 48, 48, 48], [48, 97, 96, 48, 48], [48, 48, 48, 48, 48], [35, 48, 94, 66, 4]],
    [[48, 96, 48, 48, 48], [48, 97, 49, 48, 48], [48, 79, 96, 48, 48], [48, 48, 48, 48, 48], [49, 48, 98, 62, 7]],
    [[48, 95, 49, 48, 48], [48, 97, 32, 48, 48], [48, 32, 96, 48, 48], [48, 48, 48, 48, 48], [49, 48, 98, 59, 7]],
    [[48, 95, 48, 48, 48], [48, 97, 48, 48, 48], [48, 96, 96, 48, 48], [48, 48, 48, 48, 48], [51, 48, 95, 41, 27]],
    [[48, 0, 48, 48, 48], [48, 96, 48, 48, 48], [48, 99, 97, 48, 48], [48, 48, 48, 48, 48], [48, 48, 98, 32, 44]],
    [[48, 0, 48, 48, 48], [48, 95, 48, 48, 48], [48, 98, 97, 48, 48], [48, 48, 48, 48, 48], [48, 48, 99, 20, 49]],
    [[48, 96, 48, 48, 48], [48, 96, 48, 48, 48], [48, 96, 96, 48, 48], [48, 48, 48, 48, 48], [55, 49, 99, 2, 54]],
    [[48, 7, 48, 48, 48], [48, 96, 97, 48, 48], [48, 96, 96, 48, 48], [48, 48, 48, 48, 48], [54, 49, 99, 2, 53]],
    [[48, 95, 48, 48, 48], [48, 96, 2, 48, 48], [48, 47, 96, 48, 48], [48, 48, 48, 48, 48], [49, 49, 98, 4, 51]],
]


_EMBEDDED_MATRIX_CACHE = None


def embedded_frames_available():
    return bool(EMBEDDED_FRAMES_DATA)


def get_embedded_frames():
    global _EMBEDDED_MATRIX_CACHE
    if not EMBEDDED_FRAMES_DATA:
        return []
    if _EMBEDDED_MATRIX_CACHE is None:
        frames = []
        for rows in EMBEDDED_FRAMES_DATA:
            frames.append(Matrix(rows))
        _EMBEDDED_MATRIX_CACHE = frames
    return list(_EMBEDDED_MATRIX_CACHE)


def brightness_from_pixel(value):
    """Scale an 8-bit grayscale value (0-255) to the 0-100 LED brightness range."""

    return max(0, min(MAX_BRIGHTNESS, round(value * MAX_BRIGHTNESS / 255)))


def image_to_matrix(image):
    """Convert a Pillow image to a Pybricks Matrix at the configured frame size."""

    grayscale = image.convert("L")
    resampling = getattr(Image, "Resampling", None)
    if resampling is not None:
        resized = grayscale.resize(FRAME_SIZE, resampling.BILINEAR)  # type: ignore[attr-defined]
    else:
        resized = grayscale.resize(FRAME_SIZE, Image.BILINEAR)  # type: ignore[no-member]
    width, height = FRAME_SIZE
    pixels = list(resized.getdata())

    rows = []
    for row in range(height):
        start = row * width
        end = start + width
        row_values = [brightness_from_pixel(px) for px in pixels[start:end]]
        rows.append(row_values)

    return Matrix(rows)


def load_gif_frames(path):
    """Load a GIF file and return a list of matrices representing each frame."""

    if Image is None or ImageSequence is None:
        print("Debug: Pillow not available, using built-in GIF decoder")
        return _load_gif_frames_pure(path)

    if not _file_exists(path):
        raise FileNotFoundError(f"GIF file not found: {path}")

    frames = []
    with Image.open(path) as gif:  # type: ignore[no-untyped-call]
        for frame in ImageSequence.Iterator(gif):  # type: ignore[attr-defined]
            matrix = image_to_matrix(frame)
            frames.append(matrix)

    if not frames:
        raise ValueError(f"GIF file '{path}' does not contain any frames.")

    return frames


def _load_gif_frames_pure(path):
    """Decode a GIF file without external dependencies."""

    with open(path, "rb") as gif_file:
        data = gif_file.read()

    if len(data) < 13:
        raise ValueError("GIF file too small")

    header = data[0:6]
    if header not in (b"GIF87a", b"GIF89a"):
        raise ValueError("Unsupported GIF header: %s" % header)

    width = data[6] | (data[7] << 8)
    height = data[8] | (data[9] << 8)
    packed = data[10]
    global_table_flag = packed & 0x80
    global_table_size = 2 ** ((packed & 0x07) + 1)
    background_color_index = data[11]
    # pixel aspect ratio ignored

    offset = 13
    global_color_table = None
    if global_table_flag:
        expected_len = offset + 3 * global_table_size
        if len(data) < expected_len:
            raise ValueError("Incomplete global color table")
        global_color_table = []
        for i in range(global_table_size):
            r = data[offset]
            g = data[offset + 1]
            b = data[offset + 2]
            global_color_table.append((r, g, b))
            offset += 3

    frames = []
    transparent_index = None
    delay_time = 0

    while offset < len(data):
        block_id = data[offset]
        offset += 1

        if block_id == 0x3B:  # Trailer
            break

        if block_id == 0x21:  # Extension
            if offset >= len(data):
                break
            label = data[offset]
            offset += 1

            if label == 0xF9:  # Graphics Control Extension
                if offset >= len(data):
                    break
                block_size = data[offset]
                offset += 1
                if block_size != 4:
                    offset += block_size
                else:
                    packed_fields = data[offset]
                    offset += 1
                    delay_time = data[offset] | (data[offset + 1] << 8)
                    offset += 2
                    transparent_index = data[offset]
                    offset += 1
                offset += 1  # block terminator
            else:
                # Skip other extensions
                while True:
                    if offset >= len(data):
                        break
                    block_size = data[offset]
                    offset += 1
                    if block_size == 0:
                        break
                    offset += block_size
            continue

        if block_id == 0x2C:  # Image Descriptor
            if offset + 9 > len(data):
                break
            left = data[offset] | (data[offset + 1] << 8)
            top = data[offset + 2] | (data[offset + 3] << 8)
            frame_width = data[offset + 4] | (data[offset + 5] << 8)
            frame_height = data[offset + 6] | (data[offset + 7] << 8)
            packed_fields = data[offset + 8]
            offset += 9

            local_table_flag = packed_fields & 0x80
            interlace_flag = packed_fields & 0x40
            # sort_flag = packed_fields & 0x20
            local_table_size = 2 ** ((packed_fields & 0x07) + 1)

            color_table = global_color_table
            if local_table_flag:
                color_table = []
                for _ in range(local_table_size):
                    if offset + 3 > len(data):
                        raise ValueError("Incomplete local color table")
                    r = data[offset]
                    g = data[offset + 1]
                    b = data[offset + 2]
                    color_table.append((r, g, b))
                    offset += 3

            if color_table is None:
                raise ValueError("GIF is missing a color table")

            if offset >= len(data):
                break

            min_code_size = data[offset]
            offset += 1

            compressed_blocks = []
            while True:
                if offset >= len(data):
                    break
                block_size = data[offset]
                offset += 1
                if block_size == 0:
                    break
                compressed_blocks.append(data[offset:offset + block_size])
                offset += block_size

            compressed_data = b"".join(compressed_blocks)
            indices = _gif_lzw_decompress(compressed_data, min_code_size, frame_width * frame_height)

            if interlace_flag:
                indices = _deinterlace(indices, frame_width, frame_height)

            frame_brightness = _indices_to_brightness(indices, color_table, transparent_index, frame_width, frame_height)
            downscaled = _downscale_frame(frame_brightness, frame_width, frame_height)
            frames.append(Matrix(downscaled))

            # Reset transparency for next frame unless explicitly set again
            transparent_index = None
            continue

    if not frames:
        raise ValueError("No frames decoded from GIF")

    return frames


def _gif_lzw_decompress(data, min_code_size, expected_length):
    if expected_length <= 0:
        return []

    clear_code = 1 << min_code_size
    end_code = clear_code + 1
    code_size = min_code_size + 1
    max_code_size = 12

    dictionary = {}
    for i in range(clear_code):
        dictionary[i] = [i]

    result = []
    data_len = len(data)
    byte_pos = 0
    bit_pos = 0

    def read_code(current_code_size):
        nonlocal byte_pos, bit_pos
        raw = 0
        for i in range(3):
            idx = byte_pos + i
            if idx < data_len:
                raw |= data[idx] << (8 * i)
        raw >>= bit_pos
        mask = (1 << current_code_size) - 1
        code = raw & mask
        bit_pos += current_code_size
        while bit_pos >= 8:
            bit_pos -= 8
            byte_pos += 1
        return code

    prev = []
    next_code = end_code + 1

    while True:
        if byte_pos >= data_len:
            break
        code = read_code(code_size)

        if code == clear_code:
            dictionary = {}
            for i in range(clear_code):
                dictionary[i] = [i]
            code_size = min_code_size + 1
            next_code = end_code + 1
            prev = []
            continue

        if code == end_code:
            break

        if code in dictionary:
            entry = dictionary[code][:]
        elif code == next_code and prev:
            entry = prev + [prev[0]]
        else:
            raise ValueError("Invalid LZW code: %s" % code)

        result.extend(entry)

        if prev:
            dictionary[next_code] = prev + [entry[0]]
            next_code += 1
            if next_code >= (1 << code_size) and code_size < max_code_size:
                code_size += 1

        prev = entry

        if expected_length and len(result) >= expected_length:
            break

    return result[:expected_length]


def _deinterlace(indices, width, height):
    result = [0] * (width * height)
    passes = [
        (0, 8),
        (4, 8),
        (2, 4),
        (1, 2),
    ]
    idx = 0
    for start, step in passes:
        y = start
        while y < height and idx < len(indices):
            row_start = y * width
            row_end = row_start + width
            result[row_start:row_end] = indices[idx:idx + width]
            idx += width
            y += step
    return result


def _indices_to_brightness(indices, color_table, transparent_index, width, height):
    brightness = [0] * (width * height)
    for i, index in enumerate(indices):
        if index == transparent_index:
            brightness[i] = 0
            continue
        if index >= len(color_table):
            brightness[i] = 0
            continue
        r, g, b = color_table[index]
        gray = (r * 299 + g * 587 + b * 114) // 1000
        brightness[i] = gray
    return brightness


def _downscale_frame(brightness, width, height):
    target_w, target_h = FRAME_SIZE
    matrix = []
    for ty in range(target_h):
        row = []
        source_y = int((ty + 0.5) * height / target_h)
        if source_y >= height:
            source_y = height - 1
        for tx in range(target_w):
            source_x = int((tx + 0.5) * width / target_w)
            if source_x >= width:
                source_x = width - 1
            index = source_y * width + source_x
            gray = brightness[index]
            row.append(brightness_from_pixel(gray))
        matrix.append(row)
    return matrix


def play_frames(hub, frames, fps=FPS):
    """Continuously play the provided matrices on the hub at the requested FPS."""

    frame_delay_ms = max(1, int(1000 / fps))

    print(f"Playing GIF with {len(frames)} frames at {fps} FPS...")
    while True:
        for frame in frames:
            hub.display.icon(frame)
            wait(frame_delay_ms)


def run_robot_blink(hub):
    """Fallback animation: simple blinking robot face."""

    robot_on = Matrix([
        [100, 0, 100, 0, 100],
        [0, 100, 100, 100, 0],
        [100, 100, 0, 100, 100],
        [0, 100, 50, 100, 0],
        [0, 0, 100, 0, 0],
    ])

    robot_eyes_closed = Matrix([
        [100, 0, 100, 0, 100],
        [0, 100, 100, 100, 0],
        [100, 50, 0, 50, 100],
        [0, 100, 50, 100, 0],
        [0, 0, 100, 0, 0],
    ])

    print("Playing fallback robot blink animation...")
    while True:
        hub.display.icon(robot_on)
        wait(1000)
        hub.display.icon(robot_eyes_closed)
        wait(150)
        hub.display.icon(robot_on)
        wait(1000)
        print("Blink!")


def _file_exists(path):
    try:
        with open(path, "rb"):
            return True
    except OSError:
        return False


def _resolve_env_gif():
    """Return a file path from the environment variable if available."""

    if os is None or not hasattr(os, "getenv"):
        print("Debug: OS module unavailable; skipping env lookup")
        return None

    value = os.getenv(GIF_ENV_VAR)
    if not value:
        print("Debug: %s not set" % GIF_ENV_VAR)
        return None

    path = value
    if os and hasattr(os.path, "expanduser"):
        path = os.path.expanduser(path)

    if _file_exists(path):
        print("Debug: Using GIF from env %s" % path)
        return path

    print("Warning: environment variable %s is set but file not found: %s" % (GIF_ENV_VAR, path))
    return None


def _find_default_gif():
    """Return the first available GIF using preferred filenames or any *.gif file."""

    for name in DEFAULT_GIF_CANDIDATES:
        if _file_exists(name):
            print("Debug: Found default candidate %s" % name)
            return name

    if os is not None and hasattr(os, "listdir"):
        try:
            candidates = sorted([f for f in os.listdir(".") if f.lower().endswith(".gif")])
            print("Debug: Directory GIF candidates %s" % candidates)
            for candidate in candidates:
                if _file_exists(candidate):
                    print("Debug: Using GIF from directory %s" % candidate)
                    return candidate
        except OSError as exc:
            print("Warning: Could not list directory for GIFs: %s" % exc)

    print("Debug: No GIF found; fallback will be used")
    return None


def parse_gif_argument(argv):
    """Parse CLI arguments for a GIF path.

    Accepts either `--gif path` or a positional path. Returns None if no GIF should
    be played.
    """

    args = list(argv)

    if not args:
        env_path = _resolve_env_gif()
        if env_path is not None:
            return env_path
        return _find_default_gif()

    if "--embedded" in args:
        print("Debug: --embedded flag detected")
        return EMBEDDED_SENTINEL

    if "--gif" in args:
        gif_index = args.index("--gif")
        if gif_index + 1 >= len(args):
            raise ValueError("Missing path after --gif option.")
        selected = args[gif_index + 1]
        print("Debug: --gif selected %s" % selected)
        return selected

    if "--blink" in args:
        return None

    # First positional argument treated as GIF path
    if len(args) >= 1:
        path = args[0]
        if _file_exists(path):
            print("Debug: Using positional path %s" % path)
            return path
        print("Debug: Positional path missing %s" % path)

    env_path = _resolve_env_gif()
    if env_path is not None:
        return env_path

    return _find_default_gif()


def main(argv=None):
    """Application entry point."""

    if argv is None:
        argv = []

    hub = PrimeHub()
    print("Hello World!")

    try:
        gif_path = parse_gif_argument(list(argv))
        if gif_path == EMBEDDED_SENTINEL:
            frames = get_embedded_frames()
            if frames:
                print("Debug: Playing embedded GIF data from %s" % EMBEDDED_SOURCE)
                play_frames(hub, frames, fps=EMBEDDED_FPS or FPS)
            else:
                print("Warning: Embedded frames requested but unavailable; falling back")
                run_robot_blink(hub)
        elif gif_path is not None:
            print("Debug: Loading GIF %s" % gif_path)
            frames = load_gif_frames(gif_path)
            print("Debug: Loaded %d frames" % len(frames))
            play_frames(hub, frames, fps=FPS)
        else:
            if embedded_frames_available():
                frames = get_embedded_frames()
                if frames:
                    print("Debug: No GIF path provided; using embedded frames from %s" % EMBEDDED_SOURCE)
                    play_frames(hub, frames, fps=EMBEDDED_FPS or FPS)
                else:
                    print("Warning: Embedded frame cache empty; running fallback")
                    run_robot_blink(hub)
            else:
                print("Debug: No GIF selected, running fallback")
                run_robot_blink(hub)
    except Exception as exc:
        print(f"Unable to play GIF: {exc}")
        print("Falling back to robot blink animation.")
        run_robot_blink(hub)
    finally:
        hub.display.off()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Animation stopped")
