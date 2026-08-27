import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from PIL import Image


def convert_one(path, destination, fmt, custom_name):
    base = (custom_name or Path(path).stem).strip()
    base = Path(base).stem or Path(path).stem
    extension = "jpg" if fmt == "jpeg" else fmt
    output = destination / f"{base}.{extension}"
    counter = 1
    while output.exists():
        output = destination / f"{base}_{counter}.{extension}"
        counter += 1
    with Image.open(path) as original:
        img = original.copy()
    if fmt in ("jpg", "jpeg"):
        if img.mode in ("RGBA", "LA"):
            background = Image.new("RGB", img.size, "white")
            if img.mode == "RGBA":
                background.paste(img, mask=img.getchannel("A"))
            else:
                background.paste(img.convert("RGB"), mask=img.getchannel("A"))
            img.close()
            img = background
        elif img.mode not in ("RGB", "L"):
            converted = img.convert("RGB")
            img.close()
            img = converted
    img.save(str(output), format=fmt.upper())
    img.close()
    return path, output


def process_batch(files, names, destination, fmt, cancel_event, progress_callback):
    total = len(files)
    success = []
    errors = []
    workers = min(8, max(2, os.cpu_count() or 2))
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(convert_one, path, destination, fmt, names[path]): path for path in files}
        for index, future in enumerate(as_completed(futures), start=1):
            path = futures[future]
            if cancel_event.is_set():
                for pending in futures:
                    pending.cancel()
                break
            try:
                future.result()
                success.append(path)
            except Exception as exc:
                errors.append((path, str(exc)))
            progress_callback(index, total, Path(path).name)
    return total, success, errors
