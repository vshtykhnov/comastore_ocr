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
        if forced_promo:
            grammar = (
                "Grammar (promo_args by promo):\n"
                "• NONE    → promo_args=\"\"\n"
                "• SUP     → promo_args=\"\" OR N                  (integer ≥1)\n"
                "• DISC    → promo_args= ONE of: P (0..100) | N | \"N:P\"  (e.g. 20 | 2 | \"2:40\")\n"
                "• DEALFIX → promo_args=\"N=price\"                (e.g. \"2=1.00\")\n"
                "• BXYG    → promo_args=\"X:Y\"                    (e.g. \"1:1\", \"5:5\")\n"
            )
            simplified_prompt = (
                "You will receive ONE product-promotion image. Return ONLY valid JSON with EXACTLY four keys:\n"
                "{\n  \"name\": \"<Polish name exactly as on image>\",\n  \"price\": <number OR null>,\n  "
                f"  \"promo\": \"{forced_promo}\",\n  \"promo_args\": \"<see grammar>\"\n}}\n\n"
                "Rules:\n"
                "• Use the given promo code EXACTLY as provided.\n"
                "• Infer ONLY 'name', 'price', and a valid 'promo_args' for this promo.\n"
                "• If no numeric price is visible, use null for price.\n"
                "• JSON only — no explanations.\n\n"
                + grammar
                + f"\nFocus: promo is fixed to {forced_promo}. Pick the correct promo_args format for this promo only."
            )
            return [
                {"role": "system", "content": simplified_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Promo is fixed: {forced_promo}. Extract remaining fields and promo_args."},
                        {"type": "image_url", "image_url": {"url": data_uri}},
                    ],
                },
            ]
        else:
            return [
                {"role": "system", "content": PROMPT_TEXT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract promotion details from this image."},
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
            # one correction attempt
            correction_messages = base_messages + [
                {
                    "role": "user",
                    "content": (
                        "Your previous JSON violated the schema (promo/promo_args/keys/types). "
                        "Return corrected JSON only. Do not add explanations."
                    ),
                }
            ]
            text_response = call_openai_with_json(correction_messages, use_json_response_format=True)
            obj = json.loads(text_response)
            is_valid, err = validate_label_object(obj)
            if not is_valid:
                raise ValueError(f"Schema validation failed: {err}")
        return obj


