import base64
from pathlib import Path


def encode_image_to_data_uri(image_path: Path) -> str:
    mime = "image/" + image_path.suffix.lstrip(".")
    data = image_path.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"


