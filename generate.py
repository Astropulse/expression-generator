import argparse
import base64
import os
import time
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

import requests
from PIL import Image

API_URL = "https://api.retrodiffusion.ai/v1/edit"
API_KEY_FILE = "Write API key in here.txt"
TIMEOUT = 120
MAX_RETRIES = 3

PREFIX = "make the character"

EXPRESSIONS = [
    "smile", "laughing", "crying", "angry", "surprised",
    "confused", "sad", "grinning with teeth", "disgusted", "pouting",
    "scared", "looking down in shape", "annoyed", "sleeping", "excited", "with a neutral expression"
]


def load_api_key() -> str:
    """Read the key from Write API key in here.txt or fall back to RD_API_KEY env var."""
    if os.path.isfile(API_KEY_FILE):
        with open(API_KEY_FILE, "r", encoding="utf-8") as f:
            key = f.read().strip()
            if key:
                return key
    return os.getenv("RD_API_KEY", "")


def img_to_b64(path: str) -> str:
    with Image.open(path) as img:
        if not (16 <= img.width <= 256 and 16 <= img.height <= 256):
            raise ValueError("Image must be between 16 and 256 px in both dimensions")
        buf = BytesIO()
        img.convert("RGB").save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def edit_image(expr: str, img_b64: str, headers: dict) -> bytes | None:
    payload = {
        "prompt": f"{PREFIX} {expr}",
        "inputImageBase64": img_b64
    }
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(API_URL, headers=headers, json=payload, timeout=TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            if "outputImageBase64" in data:
                return base64.b64decode(data["outputImageBase64"])
            if "base64_images" in data and data["base64_images"]:
                return base64.b64decode(data["base64_images"][0])
            return None
        except requests.exceptions.RequestException as err:
            if attempt == MAX_RETRIES:
                raise RuntimeError(f"{expr}: {err}") from err
            time.sleep(1 + attempt)


def worker(expr: str, img_b64: str, out_dir: str, headers: dict) -> str:
    try:
        png_bytes = edit_image(expr, img_b64, headers)
        if png_bytes is None:
            return f"{expr}: api returned no image"
        out_path = os.path.join(out_dir, f"{expr}.png")
        with open(out_path, "wb") as fp:
            fp.write(png_bytes)
        return f"{expr}: saved"
    except Exception as exc:
        return f"{expr}: {exc}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate facial expressions with RetroDiffusion")
    parser.add_argument("-i", "--input", required=True, help="input image path")
    parser.add_argument("-o", "--output", default="outputs", help="output directory")
    args = parser.parse_args()

    api_key = load_api_key()
    if not api_key:
        raise SystemExit("No API key found. Put it in 'Write API key in here.txt' or set RD_API_KEY.")

    os.makedirs(args.output, exist_ok=True)
    img_b64 = img_to_b64(args.input)
    headers = {"X-RD-Token": api_key}

    with ThreadPoolExecutor(max_workers=len(EXPRESSIONS)) as pool:
        for result in pool.map(lambda e: worker(e, img_b64, args.output, headers), EXPRESSIONS):
            print(result)


if __name__ == "__main__":
    main()