import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from PIL import Image


class ImageConverter:
    def __init__(self, max_workers=None):
        self.max_workers = max_workers or min(8, max(2, os.cpu_count() or 2))

    def convert_one(self, path, destination, fmt, custom_name):
        path = Path(path)
        destination = Path(destination)
        base = (custom_name or path.stem).strip()
        base = Path(base).stem or path.stem
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
        return str(path), output

    def convert_batch(self, files, names, destination, fmt, cancel_event, on_progress):
        total = len(files)
        success = []
        errors = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.convert_one, path, destination, fmt, names[path]): path
                for path in files
            }

            for index, future in enumerate(as_completed(futures), start=1):
                if cancel_event.is_set():
                    for pending in futures:
                        pending.cancel()
                    break

                path = futures[future]
                try:
                    future.result()
                    success.append(path)
                except Exception as exc:
                    errors.append((path, str(exc)))

                on_progress(index, total, Path(path).name)

        return total, success, errors
