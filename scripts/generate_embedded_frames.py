from pathlib import Path

TARGET_SIZE = (5, 5)
OUTPUT_PATH = Path("embedded_frames.json")
PY_SNIPPET_PATH = Path("embedded_frames_snippet.py")
INPUT_PATH = Path("giphy-downsized.gif")


def brightness_from_pixel(value: int) -> int:
    return round(value * 100 / 255)


def _file_exists(path: Path) -> bool:
    return path.exists() and path.is_file()


def _gif_lzw_decompress(data, min_code_size, expected_length):
    if expected_length <= 0:
        return []

    clear_code = 1 << min_code_size
    end_code = clear_code + 1
    code_size = min_code_size + 1
    max_code_size = 12

    dictionary = {i: [i] for i in range(clear_code)}

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
            dictionary = {i: [i] for i in range(clear_code)}
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
            raise ValueError(f"Invalid LZW code: {code}")

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
    passes = [(0, 8), (4, 8), (2, 4), (1, 2)]
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


def _indices_to_brightness(indices, color_table, transparent_index):
    brightness = []
    for index in indices:
        if index == transparent_index or index >= len(color_table):
            brightness.append(0)
            continue
        r, g, b = color_table[index]
        gray = (r * 299 + g * 587 + b * 114) // 1000
        brightness.append(gray)
    return brightness


def _downscale_frame(brightness, width, height):
    target_w, target_h = TARGET_SIZE
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


def decode_gif(path: Path):
    data = path.read_bytes()
    if len(data) < 13:
        raise ValueError("GIF file too small")

    header = data[0:6]
    if header not in (b"GIF87a", b"GIF89a"):
        raise ValueError(f"Unsupported GIF header: {header}")

    width = data[6] | (data[7] << 8)
    height = data[8] | (data[9] << 8)
    packed = data[10]
    global_table_flag = packed & 0x80
    global_table_size = 2 ** ((packed & 0x07) + 1)

    offset = 13
    global_color_table = None
    if global_table_flag:
        expected_len = offset + 3 * global_table_size
        if len(data) < expected_len:
            raise ValueError("Incomplete global color table")
        global_color_table = []
        for _ in range(global_table_size):
            r = data[offset]
            g = data[offset + 1]
            b = data[offset + 2]
            global_color_table.append((r, g, b))
            offset += 3

    frames = []
    transparent_index = None

    while offset < len(data):
        block_id = data[offset]
        offset += 1

        if block_id == 0x3B:
            break

        if block_id == 0x21:
            if offset >= len(data):
                break
            label = data[offset]
            offset += 1

            if label == 0xF9:
                if offset >= len(data):
                    break
                block_size = data[offset]
                offset += 1
                if block_size == 4:
                    packed_fields = data[offset]
                    offset += 1
                    offset += 2  # delay time, ignored
                    transparent_index = data[offset]
                    offset += 1
                else:
                    offset += block_size
                offset += 1
            else:
                while True:
                    if offset >= len(data):
                        break
                    block_size = data[offset]
                    offset += 1
                    if block_size == 0:
                        break
                    offset += block_size
            continue

        if block_id == 0x2C:
            if offset + 9 > len(data):
                break
            frame_width = data[offset + 4] | (data[offset + 5] << 8)
            frame_height = data[offset + 6] | (data[offset + 7] << 8)
            packed_fields = data[offset + 8]
            offset += 9

            local_table_flag = packed_fields & 0x80
            interlace_flag = packed_fields & 0x40
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

            brightness = _indices_to_brightness(indices, color_table, transparent_index)
            frame_matrix = _downscale_frame(brightness, frame_width, frame_height)
            frames.append(frame_matrix)

            transparent_index = None
            continue

    if not frames:
        raise ValueError("No frames decoded from GIF")

    return frames


def main() -> None:
    if not _file_exists(INPUT_PATH):
        raise SystemExit(f"Input GIF not found: {INPUT_PATH}")

    frames = decode_gif(INPUT_PATH)
    OUTPUT_PATH.write_text(str(frames))
    snippet = "EMBEDDED_FRAMES_DATA = " + repr(frames) + "\n"
    PY_SNIPPET_PATH.write_text(snippet)
    print(f"Wrote {len(frames)} frames to {OUTPUT_PATH}")
    print(f"Wrote Python snippet to {PY_SNIPPET_PATH}")


if __name__ == "__main__":
    main()
