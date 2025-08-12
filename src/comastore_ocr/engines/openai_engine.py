from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

import openai

from ..common import encode_image_to_data_uri
from ..openai import call_openai_with_json, PROMPT_TEXT
from ..common import validate_label_object
from .base import LabelEngine


class OpenAIEngine(LabelEngine):
    def build_messages(self, image_path: Path, forced_promo: Optional[str] = None) -> List[Dict]:
        data_uri = encode_image_to_data_uri(image_path)
        # Always use the unified 6-key schema prompt. If promo is forced, we explicitly instruct the model
        # to set promo to the forced value and follow the corresponding grammar for core/cond/nth.
        user_text = (
            f"Promo is fixed to {forced_promo}. Set \"promo\": \"{forced_promo}\" and infer valid core/cond/nth for this promo."
            if forced_promo
            else "Extract promotion details from this image."
        )
        return [
            {"role": "system", "content": PROMPT_TEXT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_text},
                    {"type": "image_url", "image_url": {"url": data_uri}},
                ],
            },
        ]

    def generate_label(self, image_path: Path, forced_promo: Optional[str] = None) -> Dict:
        base_messages = self.build_messages(image_path, forced_promo=forced_promo)
        text_response = call_openai_with_json(base_messages, use_json_response_format=True)
        obj = json.loads(text_response)
        is_valid, err = validate_label_object(obj)
        if not is_valid:
            # Show the raw first response for easier debugging
            print(f"⚠️  Raw model response (invalid) for {image_path.name}: {text_response}")
            # one correction attempt
            correction_messages = base_messages + [
                {
                    "role": "user",
                    "content": (
                        "Your previous JSON violated the schema (promo/core/cond/nth/keys/types). "
                        "Return corrected JSON only. Do not add explanations."
                    ),
                }
            ]
            text_response = call_openai_with_json(correction_messages, use_json_response_format=True)
            obj = json.loads(text_response)
            is_valid, err = validate_label_object(obj)
            if not is_valid:
                print(f"⚠️  Raw correction response (invalid) for {image_path.name}: {text_response}")
                # Include the raw response in the exception to bubble up to the CLI logs
                raise ValueError(
                    f"Schema validation failed: {err}. Raw: {text_response}"
                )
        return obj


