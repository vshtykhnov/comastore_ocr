import base64
from pathlib import Path


def encode_image_to_data_uri(image_path: Path) -> str:
    mime = "image/" + image_path.suffix.lstrip(".")
    with image_path.open("rb") as file_handle:
        b64 = base64.b64encode(file_handle.read()).decode("ascii")
    return f"data:{mime};base64,{b64}"


