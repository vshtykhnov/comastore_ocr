import re, math
from typing import Tuple

ALLOWED_PROMO_CODES = {"NONE", "SUP", "DISC", "DEALPCT", "DEALFIX", "BXYG", "PACK"}

_SINGLE_PACK = r"(?:[1-9]\d*(?::(?:100|\d{1,2}))?|[1-9]\d*x[1-9]\d*(?::(?:100|\d{1,2}))?)"

PROMO_ARGS_PATTERNS = {
    "NONE":     re.compile(r"^$"),
    "SUP":      re.compile(r"^$|^[1-9]\d*$"),
    "DISC":     re.compile(r"^(100|\d{1,2})$"),
    "DEALPCT":  re.compile(r"^[1-9]\d*:(100|\d{1,2})$"),
    "DEALFIX":  re.compile(r"^[1-9]\d*=\d+(\.\d{1,2})?$"),
    "BXYG":     re.compile(r"^[1-9]\d*:[1-9]\d*$"),
    "PACK":     re.compile(rf"^{_SINGLE_PACK}(?:\|{_SINGLE_PACK})*$"),
}

def validate_label_object(obj: object) -> Tuple[bool, str]:
    if not isinstance(obj, dict):
        return False, "not a dict"

    expected_keys = {"name", "price", "promo", "promo_args"}
    if set(obj.keys()) != expected_keys:
        return False, f"keys must be exactly {sorted(expected_keys)}"

    if not isinstance(obj["name"], str) or not obj["name"].strip():
        return False, "name must be non-empty string"

    price = obj["price"]
    if price is not None:
        if not isinstance(price, (int, float)):
            return False, "price must be number or null"
        if not math.isfinite(float(price)):
            return False, "price must be finite number"

    promo = obj["promo"]
    if promo not in ALLOWED_PROMO_CODES:
        return False, f"promo '{promo}' not in {sorted(ALLOWED_PROMO_CODES)}"

    pa = obj["promo_args"]
    if not isinstance(pa, str):
        return False, "promo_args must be string"
    if " " in pa:
        return False, "promo_args must not contain spaces"

    if not PROMO_ARGS_PATTERNS[promo].match(pa):
        return False, f"promo_args '{pa}' invalid for {promo}"

    return True, ""
