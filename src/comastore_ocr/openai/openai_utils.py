from typing import Any, Dict, List

from dotenv import load_dotenv
import openai

from ..config import OPENAI_MODEL, OPENAI_MAX_TOKENS


load_dotenv()


def call_openai_with_json(messages: List[Dict[str, Any]], use_json_response_format: bool = True) -> str:
    """Call OpenAI chat completion with optional JSON response format.

    Returns raw text content. Caller is responsible for json.loads and validation.
    """
    kwargs = dict(model=OPENAI_MODEL, messages=messages, temperature=0.0, max_tokens=OPENAI_MAX_TOKENS)
    if use_json_response_format:
        kwargs["response_format"] = {"type": "json_object"}

    try:
        resp = openai.chat.completions.create(**kwargs)
        return resp.choices[0].message.content.strip()
    except Exception:
        if use_json_response_format:
            resp = openai.chat.completions.create(
                model=OPENAI_MODEL, messages=messages, temperature=0.0, max_tokens=OPENAI_MAX_TOKENS
            )
            return resp.choices[0].message.content.strip()
        raise


